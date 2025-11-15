"""
Staff routes for hospital management system.
Includes dashboard, report management, predictions, and CRUD operations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
import sys
import os
import csv
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import DatabaseConnection
from database.models import (
    UserDAO, PatientProfileDAO, PatientReportDAO, ReportTestDAO,
    DiseaseThresholdDAO, PredictionDAO, LoginHistoryDAO
)
from predictions.prediction_engine import PredictionEngine
from webapp.ocr_utils import OCRParser, get_default_values
from utils.medical_mappings import normalize_parameter_name, get_diseases_for_symptom, is_parameter_normal, calculate_risk_score
from utils.mapping import get_disease_config
from utils.cpp_dsa_wrapper import HashMap as MedicalHashMap
import re

# Import C++ tree module
try:
    import cpp_tree
except ImportError:
    print("Warning: cpp_tree module not found.")
    cpp_tree = None

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

# Initialize OCR parser and prediction engine
ocr_parser = OCRParser()
prediction_engine = PredictionEngine()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf', 'csv'}


def staff_required(f):
    """Decorator to require staff authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'staff':
            flash('Please login as staff to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('role') == 'PATIENT':
            flash('Staff access required', 'error')
            return redirect(url_for('patient.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@staff_bp.route('/dashboard')
@staff_required
def dashboard():
    """Staff dashboard."""
    # Get statistics
    all_predictions = DatabaseConnection.execute_query(
        "SELECT COUNT(*) as count FROM predictions"
    )
    total_predictions = all_predictions[0]['count'] if all_predictions else 0
    
    stats = {
        'total_patients': len(UserDAO.get_all_patients()),
        'total_reports': len(PatientReportDAO.get_all_reports()),
        'total_predictions': total_predictions,
    }
    
    # Get recent reports
    recent_reports = PatientReportDAO.get_all_reports()[:10]
    
    return render_template('staff/dashboard.html', 
                         stats=stats, 
                         recent_reports=recent_reports,
                         user_name=session.get('name'))


@staff_bp.route('/patients')
@staff_required
def view_patients():
    """View all patients."""
    patients = UserDAO.get_all_patients()
    return render_template('staff/patients.html', patients=patients)


@staff_bp.route('/reports')
@staff_required
def view_reports():
    """View all reports."""
    reports = PatientReportDAO.get_all_reports()
    return render_template('staff/reports.html', reports=reports)


@staff_bp.route('/reports/upload', methods=['GET', 'POST'])
@staff_required
def upload_report():
    """Upload patient report (CSV/Manual/PDF)."""
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        report_type = request.form.get('report_type', 'general')
        notes = request.form.get('notes', '')
        
        if not patient_id:
            flash('Please select a patient', 'error')
            return redirect(request.url)
        
        staff_id = session.get('user_id')
        file = None
        uploaded_file_path = None
        
        # Handle file upload
        if 'report_file' in request.files:
            file = request.files['report_file']
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    uploaded_file_path = os.path.join(upload_folder, filename)
                    file.save(uploaded_file_path)
                else:
                    flash('Invalid file type', 'error')
                    return redirect(request.url)
        
        # Create report (use 'GENERAL' as report type for disease-based analysis)
        report_id = PatientReportDAO.create_report(
            patient_id=patient_id,
            staff_id=staff_id,
            report_type='GENERAL',  # Changed from report_type to GENERAL for disease analysis
            uploaded_file=uploaded_file_path,
            notes=notes
        )
        
        if report_id:
            flash('Report uploaded successfully', 'success')
            
            # Process file and extract test data (like Version 4)
            test_data = {}
            if uploaded_file_path:
                file_ext = uploaded_file_path.rsplit('.', 1)[1].lower()
                
                if file_ext == 'csv':
                    # Parse CSV with parameter normalization
                    try:
                        with open(uploaded_file_path, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            first_row = next(reader, None)
                            if first_row:
                                for key, value in first_row.items():
                                    if value and value.strip():
                                        normalized_key = normalize_parameter_name(key)
                                        try:
                                            test_data[normalized_key] = float(value.strip())
                                        except ValueError:
                                            continue
                    except Exception as e:
                        print(f"Error parsing CSV: {e}")
                else:
                    # Use OCR to extract parameters for all disease types
                    try:
                        raw_text = ocr_parser.extract_text(uploaded_file_path)
                        
                        # Extract parameters for all disease types (like Version 4)
                        disease_types = ['diabetes', 'heart', 'breast_cancer']
                        all_params = {}
                        
                        # Create medical hash map for parameter normalization
                        param_map = MedicalHashMap()
                        from utils.medical_mappings import parameter_aliases
                        for alias, standard in parameter_aliases.items():
                            param_map.put(alias, standard)
                        
                        # Extract parameters for each disease type
                        for disease_type in disease_types:
                            try:
                                patterns = ocr_parser.patterns.get(disease_type, {})
                                for field_name, field_patterns in patterns.items():
                                    for pattern in field_patterns:
                                        matches = re.finditer(pattern, raw_text, re.IGNORECASE)
                                        for match in matches:
                                            value_str = match.group(1)
                                            try:
                                                normalized = normalize_parameter_name(field_name)
                                                if value_str.lower() in ["male", "m"]:
                                                    value = 1
                                                elif value_str.lower() in ["female", "f"]:
                                                    value = 0
                                                else:
                                                    value = float(value_str)
                                                
                                                if normalized not in all_params:
                                                    all_params[normalized] = value
                                            except ValueError:
                                                continue
                            except Exception as e:
                                print(f"Error extracting parameters for {disease_type}: {e}")
                                continue
                        
                        test_data = all_params
                    except Exception as e:
                        import traceback
                        print(f"OCR extraction failed: {e}")
                        print(traceback.format_exc())
                        flash(f'OCR extraction failed: {str(e)}. Please check file format.', 'error')
                        # Don't return here - allow manual entry
            
            # Add manual test data if provided
            manual_tests = request.form.get('manual_tests')
            if manual_tests:
                # Parse manual test data (JSON format expected)
                import json
                try:
                    manual_data = json.loads(manual_tests)
                    test_data.update(manual_data)
                except:
                    pass
            
            # Save test data
            for param, value in test_data.items():
                ReportTestDAO.create_test(
                    report_id=report_id,
                    test_name=param,
                    test_value=value
                )
            
            return redirect(url_for('staff.run_prediction', report_id=report_id))
        else:
            flash('Failed to upload report', 'error')
            return redirect(request.url)
    
    # GET request - show upload form
    patients = UserDAO.get_all_patients()
    return render_template('staff/upload_report.html', patients=patients)


@staff_bp.route('/reports/<int:report_id>/predict', methods=['GET', 'POST'])
@staff_required
def run_prediction(report_id):
    """Run disease prediction on a report."""
    report = PatientReportDAO.get_report_by_id(report_id)
    
    if not report:
        flash('Report not found', 'error')
        return redirect(url_for('staff.view_reports'))
    
    # Get test data
    tests = ReportTestDAO.get_tests_by_report(report_id)
    test_data = {test['test_name']: test['test_value'] for test in tests}
    
    if request.method == 'POST':
        # Get symptoms
        symptoms = request.form.getlist('symptoms')
        symptoms_text = request.form.get('symptoms_text', '')
        
        if symptoms_text:
            symptoms.extend([s.strip() for s in symptoms_text.split(',') if s.strip()])
        
        # Get prediction type
        prediction_type = request.form.get('prediction_type', 'all')  # 'all', 'diabetes', 'heart', 'breast_cancer'
        
        predictions = []
        
        if prediction_type == 'all':
            # Predict all diseases using C++ models (like Version 4)
            results = _run_all_disease_models_cpp(test_data, symptoms)
            
            for result in results:
                # Get disease ID from name
                disease_id = _get_disease_id(result['disease_type'])
                
                if disease_id:
                    prediction_id = PredictionDAO.create_prediction(
                        report_id=report_id,
                        disease_id=disease_id,
                        prediction_result=result['prediction'],
                        confidence_score=result.get('confidence', result.get('risk_score', 50)),
                        method=result.get('method', 'C++ Decision Tree')
                    )
                    predictions.append(result)
        else:
            # Predict specific disease using C++ model
            model = _load_cpp_model(prediction_type)
            if model:
                config = get_disease_config(prediction_type)
                if config:
                    defaults = get_default_values(prediction_type)
                    features = []
                    
                    for field in config['fields']:
                        field_name = field['name']
                        value = test_data.get(field_name)
                        if value is None:
                            normalized = normalize_parameter_name(field_name)
                            value = test_data.get(normalized)
                        if value is None:
                            value = defaults.get(field_name, field.get('default', 0))
                        features.append(float(value))
                    
                    prediction = model.predict(features)
                    outcome_label = config['outcome_labels'].get(prediction, 'Unknown')
                    
                    disease_id = _get_disease_id(prediction_type)
                    if disease_id:
                        PredictionDAO.create_prediction(
                            report_id=report_id,
                            disease_id=disease_id,
                            prediction_result=prediction,
                            confidence_score=75.0,  # Default confidence
                            method='C++ Decision Tree'
                        )
                        predictions.append({
                            'disease_type': prediction_type,
                            'disease_name': config['name'],
                            'prediction': prediction,
                            'outcome': outcome_label,
                            'confidence': 75.0,
                            'method': 'C++ Decision Tree'
                        })
        
        flash(f'Predictions generated successfully', 'success')
        return render_template('staff/prediction_results.html',
                             report=report,
                             predictions=predictions,
                             test_data=test_data)
    
    # GET request - show prediction form
    return render_template('staff/run_prediction.html',
                         report=report,
                         test_data=test_data)


def _get_disease_id(disease_name):
    """Get disease ID from name."""
    query = "SELECT id FROM disease_models WHERE disease_name = %s OR disease_code = %s"
    result = DatabaseConnection.execute_query(query, (disease_name, disease_name))
    return result[0]['id'] if result else None


def _load_cpp_model(disease_type):
    """Load C++ model for disease type (like Version 4)."""
    if cpp_tree is None:
        return None
    
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(script_dir, 'models')
    model_path = os.path.join(models_dir, f'{disease_type}_model.txt')
    model_path = os.path.normpath(model_path)
    
    if not os.path.exists(model_path):
        return None
    
    try:
        model = cpp_tree.DecisionTree()
        loaded = model.load(model_path)
        if not loaded:
            return None
        return model
    except Exception as e:
        print(f"Error loading model ({model_path}): {e}")
        return None


def _run_all_disease_models_cpp(test_data, symptoms_list):
    """
    Run all three disease models using C++ (like Version 4).
    Returns list of results with predictions and risk scores.
    """
    results = []
    disease_types = ['diabetes', 'heart', 'breast_cancer']
    
    for disease_type in disease_types:
        try:
            # Load C++ model
            model = _load_cpp_model(disease_type)
            if model is None:
                continue
            
            # Get disease config
            config = get_disease_config(disease_type)
            if not config:
                continue
            
            # Extract features for this disease
            features = []
            defaults = get_default_values(disease_type)
            
            for field in config['fields']:
                field_name = field['name']
                # Try to get from test data
                value = test_data.get(field_name)
                if value is None:
                    # Try normalized name
                    normalized = normalize_parameter_name(field_name)
                    value = test_data.get(normalized)
                if value is None:
                    # Use default
                    value = defaults.get(field_name, field.get('default', 0))
                
                features.append(float(value))
            
            # Make prediction using C++ model
            prediction = model.predict(features)
            outcome_label = config['outcome_labels'].get(prediction, 'Unknown')
            
            # Check symptom correlation
            symptom_match = False
            for symptom in symptoms_list:
                diseases = get_diseases_for_symptom(symptom)
                if disease_type in diseases:
                    symptom_match = True
                    break
            
            # Check for abnormal values
            abnormal_values = False
            for i, field in enumerate(config['fields']):
                field_name = field['name']
                value = features[i] if i < len(features) else 0
                is_normal, _ = is_parameter_normal(field_name, value)
                if is_normal is False:
                    abnormal_values = True
                    break
            
            # Calculate risk score
            confidence_factors = {
                'symptom_match': symptom_match,
                'abnormal_values': abnormal_values,
                'trend_worsening': False
            }
            risk_score = calculate_risk_score(prediction, confidence_factors)
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = "CRITICAL"
                risk_emoji = "🔴"
            elif risk_score >= 40:
                risk_level = "MEDIUM"
                risk_emoji = "🟡"
            else:
                risk_level = "LOW"
                risk_emoji = "🟢"
            
            results.append({
                'disease_type': disease_type,
                'disease_name': config['name'],
                'prediction': prediction,
                'outcome': outcome_label,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_emoji': risk_emoji,
                'confidence': risk_score,  # Use risk_score as confidence
                'features': features,
                'symptom_match': symptom_match,
                'abnormal_values': abnormal_values,
                'field_names': [f['label'] for f in config['fields']],
                'method': 'C++ Decision Tree'
            })
            
        except Exception as e:
            print(f"Error running model for {disease_type}: {e}")
            continue
    
    return results


@staff_bp.route('/thresholds')
@staff_required
def view_thresholds():
    """View all disease thresholds."""
    thresholds = DiseaseThresholdDAO.get_all_thresholds()
    return render_template('staff/thresholds.html', thresholds=thresholds)


@staff_bp.route('/thresholds/add', methods=['GET', 'POST'])
@staff_required
def add_threshold():
    """Add disease threshold."""
    if request.method == 'POST':
        disease_id = request.form.get('disease_id')
        parameter_name = request.form.get('parameter_name')
        min_value = request.form.get('min_value')
        max_value = request.form.get('max_value')
        unit = request.form.get('unit', '')
        
        if not all([disease_id, parameter_name, min_value, max_value]):
            flash('Please fill all required fields', 'error')
            return redirect(request.url)
        
        threshold_id = DiseaseThresholdDAO.create_threshold(
            disease_id=disease_id,
            parameter_name=parameter_name,
            min_value=float(min_value),
            max_value=float(max_value),
            unit=unit
        )
        
        if threshold_id:
            flash('Threshold added successfully', 'success')
            return redirect(url_for('staff.view_thresholds'))
        else:
            flash('Failed to add threshold', 'error')
            return redirect(request.url)
    
    # GET request - show form
    query = "SELECT * FROM disease_models ORDER BY disease_name"
    diseases = DatabaseConnection.execute_query(query)
    return render_template('staff/add_threshold.html', diseases=diseases)


@staff_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@staff_required
def delete_report(report_id):
    """Delete a report."""
    if PatientReportDAO.delete_report(report_id):
        flash('Report deleted successfully', 'success')
    else:
        flash('Failed to delete report', 'error')
    return redirect(url_for('staff.view_reports'))

