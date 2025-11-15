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

