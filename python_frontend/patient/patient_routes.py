"""
Patient routes for hospital management system.
Includes dashboard, report history, predictions, and trend analysis.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import DatabaseConnection
from database.models import (
    PatientReportDAO, PredictionDAO, ReportTestDAO, PatientProfileDAO
)
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
    
    # Get recent predictions
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
    """View all reports."""
    patient_id = session.get('user_id')
    reports = PatientReportDAO.get_reports_by_patient(patient_id)
    
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
    test_data = {test['test_name']: test['test_value'] for test in tests}
    
    # Get predictions
    predictions = PredictionDAO.get_predictions_by_report(report_id)
    
    # Get historical data for trend analysis
    all_reports = PatientReportDAO.get_reports_by_patient(patient_id)
    historical_data = []
    
    for r in all_reports:
        if r['id'] != report_id:
            hist_tests = ReportTestDAO.get_tests_by_report(r['id'])
            hist_test_data = {t['test_name']: t['test_value'] for t in hist_tests}
            historical_data.append({
                'report_id': r['id'],
                'date': r['created_at'],
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


@patient_bp.route('/predictions')
@patient_required
def view_predictions():
    """View all predictions."""
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
        test_data = {test['test_name']: test['test_value'] for test in tests}
        report_data.append({
            'report_id': report['id'],
            'date': report['created_at'],
            'test_data': test_data
        })
    
    # Analyze trends if we have at least 2 reports
    trends = {}
    if len(report_data) >= 2:
        latest = report_data[-1]
        historical = report_data[:-1]
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
    
    return render_template('patient/medical_summary.html',
                         profile=profile,
                         reports=reports,
                         predictions=predictions)


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
            
            # Fallback to dsa_result if ML replaced top-level keys
            dsa_sub = result.get('dsa_result', {})
            template_thresholds = result.get('threshold_violations', dsa_sub.get('threshold_violations', []))
            template_symptoms = result.get('symptom_matches', dsa_sub.get('symptom_matches', 0))
            template_risk = result.get('risk_score', dsa_sub.get('risk_score', 0))

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
                                 risk_score=template_risk)
                                 
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            return redirect(request.url)
            
    # GET request
    return render_template('patient/predict_form.html', 
                         disease_name=config['name'],
                         fields=config['fields'],
                         disease_type=disease_type)

