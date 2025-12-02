"""
Patient routes for hospital management system.
Includes dashboard, report history, predictions, and trend analysis.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask import send_from_directory, abort
from functools import wraps
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import DatabaseConnection
from database.models import (
    PatientReportDAO, PredictionDAO, ReportTestDAO, PatientProfileDAO
)
from database.db_connection import DatabaseConnection
from predictions.prediction_engine import PredictionEngine
from utils.mapping import DISEASE_CONFIG

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

prediction_engine = PredictionEngine()


def patient_required(f):
    """Decorator to require patient authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'PATIENT':
            flash('Patient access required', 'error')
            return redirect(url_for('staff.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    """Patient dashboard."""
    patient_id = session.get('user_id')
    
    # Get patient profile
    profile = PatientProfileDAO.get_profile_by_patient_id(patient_id)
    
    # Get recent reports
    reports = PatientReportDAO.get_reports_by_patient(patient_id)[:5]
    
    # Get recent predictions with stored detailed analysis data
    predictions = PredictionDAO.get_predictions_by_patient(patient_id)[:5]
    
    # Statistics
    stats = {
        'total_reports': len(PatientReportDAO.get_reports_by_patient(patient_id)),
        'total_predictions': len(PredictionDAO.get_predictions_by_patient(patient_id))
    }
    
    return render_template('patient/dashboard.html',
                         profile=profile,
                         reports=reports,
                         predictions=predictions,
                         stats=stats,
                         user_name=session.get('name'))


@patient_bp.route('/reports')
@patient_required
def view_reports():
    """View all reports with enhanced data."""
    patient_id = session.get('user_id')
    reports = PatientReportDAO.get_reports_by_patient(patient_id)
    
    # Enhance each report with additional data
    for report in reports:
        # Get test count
        tests = ReportTestDAO.get_tests_by_report(report['id'])
        report['test_count'] = len(tests)
        
        # Get predictions and calculate max risk score
        predictions = PredictionDAO.get_predictions_by_report(report['id'])
        report['prediction_count'] = len(predictions)
        
        # Calculate max risk score from predictions (prioritize risk_score)
        if predictions:
            max_risk = max([p.get('risk_score') or p.get('confidence_score', 0) for p in predictions])
            report['max_risk_score'] = max_risk
        else:
            report['max_risk_score'] = None
    
    return render_template('patient/reports.html', reports=reports)



@patient_bp.route('/reports/<int:report_id>')
@patient_required
def view_report_detail(report_id):
    """View detailed report with predictions."""
    patient_id = session.get('user_id')
    
    # Get report
    report = PatientReportDAO.get_report_by_id(report_id)
    
    if not report or report['patient_id'] != patient_id:
        flash('Report not found', 'error')
        return redirect(url_for('patient.view_reports'))
    
    # Get test data
    tests = ReportTestDAO.get_tests_by_report(report_id)
    test_data = {test['test_name']: float(test['test_value']) if test['test_value'] is not None else None for test in tests}
    
    # Get predictions
    predictions = PredictionDAO.get_predictions_by_report(report_id)
    
    # Get historical data for trend analysis
    all_reports = PatientReportDAO.get_reports_by_patient(patient_id)
    historical_data = []
    
    for r in all_reports:
        if r['id'] != report_id:
            hist_tests = ReportTestDAO.get_tests_by_report(r['id'])
            hist_test_data = {t['test_name']: float(t['test_value']) if t['test_value'] is not None else None for t in hist_tests}
            
            # Convert datetime to string for JSON serialization
            report_date = r['created_at']
            if hasattr(report_date, 'strftime'):
                report_date_str = report_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                report_date_str = str(report_date) if report_date else None
            
            historical_data.append({
                'report_id': r['id'],
                'date': report_date_str,
                'test_data': hist_test_data
            })
    
    # Analyze trends
    trends = prediction_engine.analyze_trends(test_data, historical_data)
    
    return render_template('patient/report_detail.html',
                         report=report,
                         tests=tests,
                         test_data=test_data,
                         predictions=predictions,
                         trends=trends)


@patient_bp.route('/reports/<int:report_id>/file')
@patient_required
def download_report_file(report_id):
    """Serve uploaded report file for viewing/downloading."""
    patient_id = session.get('user_id')
    report = PatientReportDAO.get_report_by_id(report_id)
    
    if not report:
        abort(404)
    
    # Security check: Ensure the report belongs to the logged-in patient
    if report.get('patient_id') != patient_id:
        flash('Unauthorized access to report', 'error')
        abort(403)
    
    uploaded = report.get('uploaded_file')
    if not uploaded:
        flash('No file attached to this report', 'error')
        return redirect(url_for('patient.view_report_detail', report_id=report_id))

    # Check if download parameter is set
    download = request.args.get('download', 'false').lower() == 'true'
    
    try:
        # uploaded_file is stored as absolute path in database
        # Check if file exists at the stored path
        if os.path.isfile(uploaded):
            directory = os.path.dirname(uploaded)
            filename = os.path.basename(uploaded)
            return send_from_directory(directory, filename, as_attachment=download)
        else:
            # Fallback: try relative path from uploads folder
            upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
            filename = os.path.basename(uploaded)
            filepath = os.path.join(upload_dir, filename)
            
            if os.path.isfile(filepath):
                return send_from_directory(upload_dir, filename, as_attachment=download)
            else:
                print(f"File not found: {uploaded}")
                print(f"Also tried: {filepath}")
                flash('File not found on server', 'error')
                abort(404)
    except Exception as e:
        print(f"Error serving file: {e}")
        flash('Error loading file', 'error')
        abort(404)


@patient_bp.route('/predictions')
@patient_required
def view_predictions():
    """View all predictions with stored detailed analysis data."""
    patient_id = session.get('user_id')
    predictions = PredictionDAO.get_predictions_by_patient(patient_id)
    
    return render_template('patient/predictions.html', predictions=predictions)


@patient_bp.route('/trends')
@patient_required
def view_trends():
    """View trend analysis."""
    patient_id = session.get('user_id')
    
    # Get all reports
    reports = PatientReportDAO.get_reports_by_patient(patient_id)
    
    # Get test data for all reports
    report_data = []
    for report in reports:
        tests = ReportTestDAO.get_tests_by_report(report['id'])
        # Convert Decimal to float for JSON serialization
        test_data = {}
        for test in tests:
            test_value = test['test_value']
            # Convert Decimal to float
            if test_value is not None:
                test_data[test['test_name']] = float(test_value)
            else:
                test_data[test['test_name']] = None
        
        # Convert datetime to string for JSON serialization
        report_date = report['created_at']
        if hasattr(report_date, 'strftime'):
            report_date_str = report_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            report_date_str = str(report_date) if report_date else None
        
        report_data.append({
            'report_id': report['id'],
            'date': report_date_str,
            'test_data': test_data
        })
    
    # Analyze trends if we have at least 2 reports
    trends = {}
    if len(report_data) >= 2:
        latest = report_data[0]  # Most recent report
        historical = report_data[1:]  # Older reports (newest first)
        trends = prediction_engine.analyze_trends(latest['test_data'], historical)
    
    return render_template('patient/trends.html',
                         reports=reports,
                         report_data=report_data,
                         trends=trends)




@patient_bp.route('/summary')
@patient_required
def medical_summary():
    """Generate medical summary (printable/downloadable)."""
    patient_id = session.get('user_id')
    
    # Get profile
    profile = PatientProfileDAO.get_profile_by_patient_id(patient_id)
    
    # Get all reports
    reports = PatientReportDAO.get_reports_by_patient(patient_id)
    
    # Get all predictions
    predictions = PredictionDAO.get_predictions_by_patient(patient_id)
    
    # Calculate statistics
    high_risk_count = len([p for p in predictions if (p.get('risk_score') or p.get('confidence_score', 0)) >= 70])
    medium_risk_count = len([p for p in predictions if 40 <= (p.get('risk_score') or p.get('confidence_score', 0)) < 70])
    low_risk_count = len([p for p in predictions if (p.get('risk_score') or p.get('confidence_score', 0)) < 40])
    
    statistics = {
        'total_reports': len(reports),
        'total_predictions': len(predictions),
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count
    }
    
    return render_template('patient/medical_summary.html',
                         profile=profile,
                         reports=reports,
                         predictions=predictions,
                         statistics=statistics,
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M'))


# ============================================================================
# DISEASE DETECTION (Patient)
# ============================================================================

@patient_bp.route('/disease-detection', methods=['GET'])
@patient_required
def disease_selection():
    """Render disease selection page for Patient."""
    return render_template('patient/disease_selection.html')

@patient_bp.route('/predict/<disease_type>', methods=['GET', 'POST'])
@patient_required
def predict_disease(disease_type):
    """
    Handle disease prediction for Patient.
    GET: Render the input form.
    POST: Process form data and show results.
    """
    if disease_type not in DISEASE_CONFIG:
        flash('Invalid disease type', 'error')
        return redirect(url_for('patient.disease_selection'))
    
    config = DISEASE_CONFIG[disease_type]
    
    if request.method == 'POST':
        try:
            # Extract features from form
            form_data = request.form.to_dict()
            
            # Convert to appropriate types
            test_data = {}
            for field in config['fields']:
                field_name = field['name']
                value = form_data.get(field_name)
                if value:
                    try:
                        test_data[field_name] = float(value)
                    except ValueError:
                        continue
            
            # Get symptoms (optional)
            symptoms = [] 
            
            # Run prediction
            result = prediction_engine.predict(test_data, symptoms, disease_type)
            
            # Save prediction to database
            try:
                # Get disease_id from disease_type
                disease_id = _get_disease_id_for_patient(disease_type)
                
                if disease_id:
                    # Create a self-prediction report using existing schema
                    # Use patient_id as staff_id for self-predictions (workaround)
                    report_type_map = {
                        'diabetes': 'DIABETES',
                        'heart': 'HEART', 
                        'breast_cancer': 'BREAST_CANCER'
                    }
                    db_report_type = report_type_map.get(disease_type, 'GENERAL')
                    
                    report_id = PatientReportDAO.create_report(
                        patient_id=session.get('user_id'),
                        staff_id=session.get('user_id'),  # Workaround: use patient as staff for self-predictions
                        report_type=db_report_type,
                        notes=f'Patient self-prediction for {disease_type}'
                    )
                    
                    if report_id:
                        # Save test data to report_tests
                        for test_name, test_value in test_data.items():
                            ReportTestDAO.create_test(
                                report_id=report_id,
                                test_name=test_name,
                                test_value=float(test_value),
                                reference_range='Patient Input',
                                unit='Various'
                            )
                        
                        # Save prediction
                        PredictionDAO.create_prediction(
                            report_id=report_id,
                            disease_id=disease_id,
                            prediction_result=result.get('prediction', 0),
                            confidence_score=result.get('confidence', result.get('risk_score', 50.0)),
                            method='DSA'
                        )
            except Exception as e:
                print(f"Error saving patient prediction: {e}")
                # Continue with displaying results even if saving fails
            
            # Get DSA result details for template display
            dsa_sub = result.get('dsa_result', {})
            template_thresholds = result.get('threshold_violations', dsa_sub.get('threshold_violations', []))
            template_symptoms = result.get('symptom_matches', dsa_sub.get('symptom_matches', 0))
            template_risk = result.get('risk_score', dsa_sub.get('risk_score', 0))
            template_severity = result.get('severity_label', dsa_sub.get('severity_label', None))
            template_severity_reason = result.get('severity_reason', dsa_sub.get('severity_reason', ''))

            # Render result
            return render_template('patient/predict_result.html', 
                                 prediction=result.get('prediction', 0),
                                 outcome=config['outcome_labels'].get(result.get('prediction', 0), ''),
                                 remark=result.get('remark', 'Based on the analysis of provided health metrics.'),
                                 features=list(test_data.values()),
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
    return render_template('patient/predict_form.html', 
                         disease_name=config['name'],
                         fields=config['fields'],
                         disease_type=disease_type)


def _get_disease_id_for_patient(disease_type):
    """Get disease ID for a given disease type."""
    # Map disease_type to database disease_name/disease_code
    disease_map = {
        'diabetes': 'Diabetes',
        'heart': 'Heart Disease', 
        'breast_cancer': 'Breast Cancer'
    }
    
    disease_name = disease_map.get(disease_type)
    if not disease_name:
        return None
        
    try:
        query = "SELECT id FROM disease_models WHERE disease_name = %s OR disease_code = %s"
        result = DatabaseConnection.execute_query(query, (disease_name, disease_type))
        return result[0]['id'] if result else None
    except Exception as e:
        print(f"Error getting disease ID: {e}")
        return None

