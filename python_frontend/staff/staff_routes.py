"""
Staff routes for hospital management system.
Includes dashboard, report management, predictions, and CRUD operations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from functools import wraps
import sys
import os
import csv
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import DatabaseConnection
from database.models import (
    UserDAO, PatientProfileDAO, PatientReportDAO, ReportTestDAO,
    DiseaseThresholdDAO, PredictionDAO
)
from predictions.prediction_engine import PredictionEngine
from ocr_utils import OCRParser, get_default_values
from utils.medical_mappings import normalize_parameter_name, get_diseases_for_symptom, is_parameter_normal, calculate_risk_score
from utils.mapping import get_disease_config, DISEASE_CONFIG
from utils.cpp_dsa_wrapper import MedicalHashMap
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
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is staff (DOCTOR, LAB_TECH, or ADMIN)
        role = session.get('role')
        if role not in ['DOCTOR', 'LAB_TECH', 'ADMIN']:
            flash('Staff access required', 'error')
            if role == 'PATIENT':
                return redirect(url_for('patient.dashboard'))
            return redirect(url_for('auth.login'))
        
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
                    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads')
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


@staff_bp.route('/reports/<int:report_id>')
@staff_required
def view_report_detail(report_id):
    """View report details."""
    report = PatientReportDAO.get_report_by_id(report_id)
    if not report:
        flash('Report not found', 'error')
        return redirect(url_for('staff.view_reports'))
    
    # Get test data
    tests = ReportTestDAO.get_tests_by_report(report_id)
    
    # Get predictions
    predictions = PredictionDAO.get_predictions_by_report(report_id)
    
    return render_template('staff/report_detail.html', 
                         report=report, 
                         tests=tests, 
                         predictions=predictions)


@staff_bp.route('/reports/<int:report_id>/download')
@staff_required
def download_report_file(report_id):
    """Download report file."""
    report = PatientReportDAO.get_report_by_id(report_id)
    if not report or not report['uploaded_file']:
        flash('File not found', 'error')
        return redirect(url_for('staff.view_report_detail', report_id=report_id))
    
    try:
        return send_file(report['uploaded_file'], as_attachment=False)
    except Exception as e:
        flash(f'Error downloading file: {e}', 'error')
        return redirect(url_for('staff.view_report_detail', report_id=report_id))


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
                        method=result.get('method', 'C++ Decision Tree'),
                        show_in_patient_panel=True,  # Automatically show doctor predictions in patient panel
                        risk_score=result.get('risk_score'),
                        severity_label=result.get('severity_label', 'Unknown'),
                        severity_reason=result.get('severity_reason', ''),
                        threshold_violations=result.get('threshold_violations', []),
                        symptom_matches=result.get('symptom_matches', 0)
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
                    from utils.medical_mappings import parameter_aliases

                    def _resolve_test_value(td, fname):
                        if fname in td:
                            return td[fname]
                        n = normalize_parameter_name(fname)
                        if n in td:
                            return td[n]
                        for alias, standard in parameter_aliases.items():
                            if standard == fname:
                                a_norm = normalize_parameter_name(alias)
                                if a_norm in td:
                                    return td[a_norm]
                                if alias in td:
                                    return td[alias]
                        return defaults.get(fname, field.get('default', 0))

                    for field in config['fields']:
                        field_name = field['name']
                        value = _resolve_test_value(test_data, field_name)
                        try:
                            features.append(float(value))
                        except Exception:
                            features.append(float(defaults.get(field_name, field.get('default', 0))))
                    
                    prediction = model.predict(features)
                    outcome_label = config['outcome_labels'].get(prediction, 'Unknown')
                    
                    disease_id = _get_disease_id(prediction_type)
                    if disease_id:
                        PredictionDAO.create_prediction(
                            report_id=report_id,
                            disease_id=disease_id,
                            prediction_result=prediction,
                            confidence_score=75.0,  # Default confidence
                            method='C++ Decision Tree',
                            show_in_patient_panel=True  # Automatically show doctor predictions in patient panel
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
            
            # Extract features for this disease (resolve values robustly)
            features = []
            defaults = get_default_values(disease_type)

            # helper to resolve a field value from various possible keys
            from utils.medical_mappings import parameter_aliases

            def _resolve_test_value(td, fname):
                # direct match
                if fname in td:
                    return td[fname]
                # normalized match
                n = normalize_parameter_name(fname)
                if n in td:
                    return td[n]
                # try aliases mapping (alias -> standard)
                for alias, standard in parameter_aliases.items():
                    if standard == fname:
                        a_norm = normalize_parameter_name(alias)
                        if a_norm in td:
                            return td[a_norm]
                        if alias in td:
                            return td[alias]
                # finally use defaults
                return defaults.get(fname, field.get('default', 0))

            for field in config['fields']:
                field_name = field['name']
                value = _resolve_test_value(test_data, field_name)
                try:
                    features.append(float(value))
                except Exception:
                    features.append(float(defaults.get(field_name, field.get('default', 0))) )
            
            # Debug: show resolved feature mapping for this disease
            try:
                print(f"[DEBUG] {disease_type} features: {list(zip([f['name'] for f in config['fields']], features))}")
            except Exception:
                pass

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
            
            # Run detailed DSA analysis for threshold violations and severity
            try:
                dsa_result = prediction_engine.analyze_with_dsa(test_data, symptoms_list, disease_type)
                threshold_violations = dsa_result.get('threshold_violations', [])
                symptom_matches = dsa_result.get('symptom_matches', 0)
                severity_label = dsa_result.get('severity_label', 'Unknown')
                severity_reason = dsa_result.get('severity_reason', '')
            except Exception as e:
                print(f"Error in DSA analysis for {disease_type}: {e}")
                threshold_violations = []
                symptom_matches = 0
                severity_label = 'Unknown'
                severity_reason = ''
            
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
                'method': 'C++ Decision Tree',
                'threshold_violations': threshold_violations,
                'symptom_matches': symptom_matches,
                'severity_label': severity_label,
                'severity_reason': severity_reason
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


# ============================================================================
# DISEASE DETECTION (Staff)
# ============================================================================

@staff_bp.route('/disease-detection', methods=['GET'])
@staff_required
def disease_selection():
    """Render disease selection page for Staff."""
    return render_template('staff/disease_selection.html')

@staff_bp.route('/predict/<disease_type>', methods=['GET', 'POST'])
@staff_required
def predict_disease(disease_type):
    """
    Handle disease prediction for Staff.
    GET: Render the input form with patient selection.
    POST: Process form data, save prediction, and show results.
    """
    if disease_type not in DISEASE_CONFIG:
        flash('Invalid disease type', 'error')
        return redirect(url_for('staff.disease_selection'))
    
    config = DISEASE_CONFIG[disease_type]
    
    if request.method == 'POST':
        try:
            test_data = {}
            file_uploaded = False
            
            # Check if file was uploaded (OCR mode)
            if 'report_file' in request.files:
                file = request.files['report_file']
                # Only process file if it has a filename (user actually selected a file)
                if file and file.filename and file.filename.strip() and allowed_file(file.filename):
                    file_uploaded = True
                    # Save uploaded file
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    uploaded_file_path = os.path.join(upload_folder, filename)
                    file.save(uploaded_file_path)
                    
                    # Extract data from file
                    file_ext = uploaded_file_path.rsplit('.', 1)[1].lower()
                    
                    if file_ext == 'csv':
                        # Parse CSV
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
                            flash(f'Error parsing CSV: {str(e)}', 'error')
                            return redirect(request.url)
                    else:
                        # Use OCR for PDF/Images
                        try:
                            raw_text = ocr_parser.extract_text(uploaded_file_path)
                            
                            # Extract parameters for the specific disease type
                            patterns = ocr_parser.patterns.get(disease_type, {})
                            param_map = MedicalHashMap()
                            from utils.medical_mappings import parameter_aliases
                            for alias, standard in parameter_aliases.items():
                                param_map.put(alias, standard)
                            
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
                                            
                                            if normalized not in test_data:
                                                test_data[normalized] = value
                                        except ValueError:
                                            continue
                        except Exception as e:
                            flash(f'OCR extraction failed: {str(e)}', 'error')
                            return redirect(request.url)
                    
                    # Clean up uploaded file
                    if os.path.exists(uploaded_file_path):
                        try:
                            os.remove(uploaded_file_path)
                        except:
                            pass
                    
                    # Store extracted data in session and redirect to review page
                    session['ocr_extracted_data'] = test_data
                    session['disease_type_for_review'] = disease_type
                    # Also store patient_id if selected
                    session['selected_patient_id'] = request.form.get('patient_id')
                    return redirect(url_for('staff.ocr_review', disease_type=disease_type))
            
            # If no file uploaded, extract from manual form
            if not file_uploaded:
                form_data = request.form.to_dict()
                for field in config['fields']:
                    field_name = field['name']
                    value = form_data.get(field_name)
                    if value:
                        try:
                            test_data[field_name] = float(value)
                        except ValueError:
                            continue
            
            # Get symptoms (optional)
            symptoms_text = request.form.get('symptoms_text', '')
            symptoms = [s.strip() for s in symptoms_text.split(',') if s.strip()] 
            
            # Run prediction
            result = prediction_engine.predict(test_data, symptoms, disease_type)
            
            # Build features list in correct order
            features = []
            for field in config['fields']:
                features.append(test_data.get(field['name'], field.get('default', 0)))
            
            # Get DSA result details for template display
            dsa_sub = result.get('dsa_result', {})
            template_thresholds = result.get('threshold_violations', dsa_sub.get('threshold_violations', []))
            template_symptoms = result.get('symptom_matches', dsa_sub.get('symptom_matches', 0))
            template_risk = result.get('risk_score', dsa_sub.get('risk_score', 0))
            template_severity = result.get('severity_label', dsa_sub.get('severity_label', None))
            template_severity_reason = result.get('severity_reason', dsa_sub.get('severity_reason', ''))

            # Save prediction if patient is selected
            patient_id = request.form.get('patient_id')
            if patient_id:
                try:
                    staff_id = session.get('user_id')
                    # Create report
                    report_id = PatientReportDAO.create_report(
                        patient_id=int(patient_id),
                        staff_id=staff_id,
                        report_type='GENERAL',
                        uploaded_file=None,
                        notes=f"Staff prediction for {disease_type}"
                    )
                    
                    # Get disease ID
                    disease_id = _get_disease_id(disease_type)
                    
                    if report_id and disease_id:
                        # Save prediction
                        PredictionDAO.create_prediction(
                            report_id=report_id,
                            disease_id=disease_id,
                            prediction_result=int(result.get('prediction', 0)),
                            confidence_score=float(result.get('confidence', 0)),
                            method=result.get('method', 'DSA'),
                            show_in_patient_panel=True,
                            risk_score=template_risk,
                            severity_label=template_severity,
                            severity_reason=template_severity_reason,
                            threshold_violations=template_thresholds,
                            symptom_matches=template_symptoms
                        )
                        
                        # Save test data
                        for param, value in test_data.items():
                            ReportTestDAO.create_test(report_id, param, value)
                            
                except Exception as e:
                    print(f"Error saving prediction: {e}")
                    # Don't fail the request, just log error

            # Render result
            return render_template('staff/predict_result.html', 
                                 prediction=result.get('prediction', 0),
                                 outcome=config['outcome_labels'].get(result.get('prediction', 0), ''),
                                 remark=result.get('remark', 'Based on the analysis of provided health metrics.'),
                                 features=features,
                                 field_names=[f['label'] for f in config['fields']],
                                 disease_name=config['name'],
                                 disease_type=disease_type,
                                 threshold_violations=template_thresholds,
                                 symptom_matches=template_symptoms,
                                 risk_score=template_risk,
                                 severity_label=template_severity,
                                 severity_reason=template_severity_reason)
                                  
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            return redirect(request.url)
            
    # GET request
    patients = UserDAO.get_all_patients()
    return render_template('staff/predict_form.html', 
                         disease_name=config['name'],
                         fields=config['fields'],
                         disease_type=disease_type,
                         patients=patients)


@staff_bp.route('/predict/<disease_type>/ocr-review', methods=['GET', 'POST'])
@staff_required
def ocr_review(disease_type):
    """
    OCR Review Page - Display extracted data for user verification.
    GET: Show review form with extracted data.
    POST: Process reviewed data and run prediction.
    """
    if disease_type not in DISEASE_CONFIG:
        flash('Invalid disease type', 'error')
        return redirect(url_for('staff.disease_selection'))
    
    config = DISEASE_CONFIG[disease_type]
    
    # Get extracted data from session
    extracted_data = session.get('ocr_extracted_data', {})
    stored_disease_type = session.get('disease_type_for_review')
    
    # Verify disease type matches
    if stored_disease_type != disease_type:
        flash('Session mismatch. Please upload the file again.', 'error')
        return redirect(url_for('staff.predict_disease', disease_type=disease_type))
    
    if request.method == 'POST':
        # User has reviewed and confirmed the data
        # Extract data from form (user may have edited values)
        test_data = {}
        form_data = request.form.to_dict()
        
        for field in config['fields']:
            field_name = field['name']
            value = form_data.get(field_name)
            if value:
                try:
                    test_data[field_name] = float(value)
                except ValueError:
                    continue
        
        # Get symptoms (optional)
        symptoms_text = request.form.get('symptoms_text', '')
        symptoms = [s.strip() for s in symptoms_text.split(',') if s.strip()] 
        
        # Run prediction
        try:
            result = prediction_engine.predict(test_data, symptoms, disease_type)
            
            # Build features list in correct order
            features = []
            for field in config['fields']:
                features.append(test_data.get(field['name'], field.get('default', 0)))
            
            # Get DSA result details for template display
            dsa_sub = result.get('dsa_result', {})
            template_thresholds = result.get('threshold_violations', dsa_sub.get('threshold_violations', []))
            template_symptoms = result.get('symptom_matches', dsa_sub.get('symptom_matches', 0))
            template_risk = result.get('risk_score', dsa_sub.get('risk_score', 0))
            template_severity = result.get('severity_label', dsa_sub.get('severity_label', None))
            template_severity_reason = result.get('severity_reason', dsa_sub.get('severity_reason', ''))

            # Save prediction if patient is selected
            patient_id = session.get('selected_patient_id')
            if patient_id:
                try:
                    staff_id = session.get('user_id')
                    # Create report
                    report_id = PatientReportDAO.create_report(
                        patient_id=int(patient_id),
                        staff_id=staff_id,
                        report_type='GENERAL',
                        uploaded_file=None,
                        notes=f"Staff prediction via OCR for {disease_type}"
                    )
                    
                    # Get disease ID
                    disease_id = _get_disease_id(disease_type)
                    
                    if report_id and disease_id:
                        # Save prediction
                        PredictionDAO.create_prediction(
                            report_id=report_id,
                            disease_id=disease_id,
                            prediction_result=int(result.get('prediction', 0)),
                            confidence_score=float(result.get('confidence', 0)),
                            method=result.get('method', 'DSA'),
                            show_in_patient_panel=True,
                            risk_score=template_risk,
                            severity_label=template_severity,
                            severity_reason=template_severity_reason,
                            threshold_violations=template_thresholds,
                            symptom_matches=template_symptoms
                        )
                        
                        # Save test data
                        for param, value in test_data.items():
                            ReportTestDAO.create_test(report_id, param, value)
                            
                except Exception as e:
                    print(f"Error saving OCR prediction: {e}")

            # Clear session data
            session.pop('ocr_extracted_data', None)
            session.pop('disease_type_for_review', None)
            session.pop('selected_patient_id', None)
            
            # Render result
            return render_template('staff/predict_result.html', 
                                 prediction=result.get('prediction', 0),
                                 outcome=config['outcome_labels'].get(result.get('prediction', 0), ''),
                                 remark=result.get('remark', 'Based on the analysis of provided health metrics.'),
                                 features=features,
                                 field_names=[f['label'] for f in config['fields']],
                                 disease_name=config['name'],
                                 disease_type=disease_type,
                                 threshold_violations=template_thresholds,
                                 symptom_matches=template_symptoms,
                                 risk_score=template_risk,
                                 severity_label=template_severity,
                                 severity_reason=template_severity_reason)
                                  
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            return redirect(url_for('staff.predict_disease', disease_type=disease_type))
    
    # GET request - Show review form
    # Prepare fields with extracted values and defaults
    defaults = get_default_values(disease_type)
    fields_with_values = []
    auto_filled_count = 0
    default_count = 0
    
    for field in config['fields']:
        field_name = field['name']
        field_copy = field.copy()
        
        # Try to get value from extracted data
        value = None
        is_auto_filled = False
        
        # Check direct match
        if field_name in extracted_data:
            value = extracted_data[field_name]
            is_auto_filled = True
        else:
            # Check normalized match
            normalized = normalize_parameter_name(field_name)
            if normalized in extracted_data:
                value = extracted_data[normalized]
                is_auto_filled = True
        
        # If not found, use default
        if value is None:
            value = defaults.get(field_name, field.get('default', 0))
            is_auto_filled = False
        
        field_copy['value'] = value
        field_copy['is_auto_filled'] = is_auto_filled
        fields_with_values.append(field_copy)
        
        if is_auto_filled:
            auto_filled_count += 1
        else:
            default_count += 1
    
    return render_template('staff/ocr_review.html',
                         disease_name=config['name'],
                         disease_type=disease_type,
                         fields=fields_with_values,
                         auto_filled_count=auto_filled_count,
                         default_count=default_count,
                         total_count=len(fields_with_values))



