"""
General disease analysis route handler.
Processes complete medical reports and runs all disease models simultaneously.
"""

import os
import sys
import csv
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.cpp_dsa_wrapper import Stack, MedicalPriorityQueue, MedicalHashMap
from utils.medical_mappings import (
    normalize_parameter_name,
    get_diseases_for_symptom,
    is_parameter_normal,
    calculate_risk_score,
    parameter_aliases,
    symptom_disease_map,
    normal_ranges
)
from ocr_utils import OCRParser, get_default_values
from utils.mapping import get_disease_config

# Import C++ tree module
try:
    import cpp_tree
except ImportError:
    print("Warning: cpp_tree module not found.")
    cpp_tree = None

# Create blueprint
general_analysis_bp = Blueprint('general_analysis', __name__)

# Initialize OCR parser
ocr_parser = OCRParser()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf', 'csv'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_model(disease_type):
    """Load a trained model from disk."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, '..', 'models')
    model_path = os.path.join(models_dir, f'{disease_type}_model.txt')
    model_path = os.path.normpath(model_path)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"C++ model not found: {model_path}. Please run train.py to train the model.")
    
    model = cpp_tree.DecisionTree()
    if not model.load(model_path):
        raise RuntimeError(f"Failed to load C++ model from {model_path}")
    
    return model


def extract_all_parameters_from_text(text, disease_types):
    """
    Extract all parameters from OCR text for all disease types.
    Returns dict with normalized parameter names and values.
    """
    all_params = {}
    
    # Create medical hash map for parameter normalization
    param_map = MedicalHashMap()
    for alias, standard in parameter_aliases.items():
        param_map.put(alias, standard)
    
    # Try to extract parameters for each disease type
    for disease_type in disease_types:
        try:
            # Use OCR parser patterns for each disease
            patterns = ocr_parser.patterns.get(disease_type, {})
            for field_name, field_patterns in patterns.items():
                for pattern in field_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        value_str = match.group(1)
                        try:
                            # Normalize field name
                            normalized = normalize_parameter_name(field_name)
                            # Convert value
                            if value_str.lower() in ["male", "m"]:
                                value = 1
                            elif value_str.lower() in ["female", "f"]:
                                value = 0
                            else:
                                value = float(value_str)
                            
                            # Store if not already present (first match wins)
                            if normalized not in all_params:
                                all_params[normalized] = value
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error extracting parameters for {disease_type}: {e}")
            continue
    
    return all_params


def parse_csv_file(filepath):
    """Parse CSV file and extract all medical parameters from first row."""
    params = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Get first row (patient data)
            first_row = next(reader, None)
            if first_row:
                for key, value in first_row.items():
                    if value and value.strip():
                        normalized_key = normalize_parameter_name(key)
                        try:
                            params[normalized_key] = float(value.strip())
                        except ValueError:
                            continue
    except Exception as e:
        print(f"Error parsing CSV: {e}")
    return params


def get_report_history_stack():
    """Get or create report history stack in session."""
    if 'report_history' not in session:
        session['report_history'] = []
    return session['report_history']


def save_report_to_history(report_data):
    """Save report to session history (Stack implementation)."""
    history = get_report_history_stack()
    
    # Add timestamp
    report_data['timestamp'] = datetime.now().isoformat()
    
    # Add to history (Stack: append to end)
    history.append(report_data)
    
    # Keep only last 5 reports (Stack max size)
    if len(history) > 5:
        history.pop(0)  # Remove oldest
    
    session['report_history'] = history


def analyze_trends(current_params, history):
    """Analyze trends by comparing current parameters with history."""
    trends = {}
    
    if not history or len(history) < 1:
        return trends
    
    # Get most recent report
    last_report = history[-1]
    last_params = last_report.get('parameters', {})
    
    for param_name, current_value in current_params.items():
        if param_name in last_params:
            last_value = last_params[param_name]
            if isinstance(current_value, (int, float)) and isinstance(last_value, (int, float)):
                change = current_value - last_value
                change_percent = (change / last_value * 100) if last_value != 0 else 0
                
                # Determine trend
                if abs(change_percent) < 5:
                    trend = "stable"
                    trend_symbol = "→"
                elif change_percent > 0:
                    trend = "increasing"
                    trend_symbol = "↑"
                else:
                    trend = "decreasing"
                    trend_symbol = "↓"
                
                trends[param_name] = {
                    'current': current_value,
                    'previous': last_value,
                    'change': change,
                    'change_percent': round(change_percent, 1),
                    'trend': trend,
                    'symbol': trend_symbol
                }
    
    return trends


def run_all_disease_models(all_params, symptoms_list):
    """Run all disease models and return a list of result dictionaries.

    Each result contains prediction, risk score, risk level, and related metadata.
    Uses the same prediction engine as separate disease predictions for consistency.
    """
    results = []
    disease_types = ['diabetes', 'heart', 'breast_cancer']
    
    # Import prediction engine for consistent predictions
    from predictions.prediction_engine import PredictionEngine
    engine = PredictionEngine()

    for disease_type in disease_types:
        try:
            # Retrieve disease configuration
            config = get_disease_config(disease_type)
            if not config:
                continue

            # Build disease-specific parameters using only relevant fields
            # This ensures each disease gets correct parameters with its own defaults
            disease_params = {}
            defaults = get_default_values(disease_type)
            
            for field in config['fields']:
                field_name = field['name']
                # Check if parameter was provided in all_params
                if field_name in all_params:
                    disease_params[field_name] = all_params[field_name]
                else:
                    # Try normalized name
                    normalized = normalize_parameter_name(field_name)
                    if normalized in all_params:
                        disease_params[field_name] = all_params[normalized]
                    else:
                        # Use disease-specific default
                        disease_params[field_name] = defaults.get(field_name, field.get('default', 0))
            
            # Use the same prediction engine as separate predictions
            dsa_result = engine.predict(disease_params, symptoms_list, disease_type)
            
            if not dsa_result:
                continue
            
            # Extract prediction data
            prediction = dsa_result.get('prediction', 0)
            outcome_label = config['outcome_labels'].get(prediction, 'Unknown')
            risk_score = dsa_result.get('risk_score', dsa_result.get('confidence', 0))
            severity_label = dsa_result.get('severity_label', 'Low')
            
            # Map severity_label to risk level and emoji for consistency
            severity_lower = severity_label.lower()
            if 'high' in severity_lower or 'critical' in severity_lower:
                risk_level = "CRITICAL"
                risk_emoji = "🔴"
            elif 'moderate' in severity_lower or 'medium' in severity_lower:
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
                'severity_label': severity_label,
                'severity_reason': dsa_result.get('severity_reason', ''),
                'threshold_violations': dsa_result.get('threshold_violations', []),
                'symptom_matches': dsa_result.get('symptom_matches', 0),
                'symptom_match': dsa_result.get('symptom_matches', 0) > 0,
                'abnormal_values': len(dsa_result.get('threshold_violations', [])) > 0,
                'method': dsa_result.get('method', 'DSA'),
                'field_names': [f['label'] for f in config['fields']]
            })
        except Exception as e:
            print(f"Error running model for {disease_type}: {e}")
            import traceback
            traceback.print_exc()
            continue
    return results


@general_analysis_bp.route('/general-analysis', methods=['GET', 'POST'])
def general_analysis():
    """Main route for general health analysis."""
    
    if request.method == 'POST':
        try:
            # Get symptoms from form
            symptoms_checkboxes = request.form.getlist('symptoms')
            symptoms_text = request.form.get('symptoms_text', '').strip()
            
            # Combine symptoms
            all_symptoms = symptoms_checkboxes.copy()
            if symptoms_text:
                # Split by comma and clean
                text_symptoms = [s.strip() for s in symptoms_text.split(',') if s.strip()]
                all_symptoms.extend(text_symptoms)
            
            # Check if file was uploaded
            file = None
            filepath = None
            extracted_params = {}
            
            if 'medical_report' in request.files:
                file = request.files['medical_report']
                
                if file and file.filename:
                    if not allowed_file(file.filename):
                        flash('Invalid file type. Please upload PDF, image, or CSV file.', 'error')
                        return redirect(request.url)
                    
                    # Save file
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    
                    # Extract parameters based on file type
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    
                    if file_ext == 'csv':
                        extracted_params = parse_csv_file(filepath)
                    else:
                        # Use OCR for images/PDFs
                        try:
                            # Extract text using OCR
                            raw_text = ocr_parser.extract_text(filepath)
                            
                            # Extract parameters for all disease types
                            disease_types = ['diabetes', 'heart', 'breast_cancer']
                            extracted_params = extract_all_parameters_from_text(raw_text, disease_types)
                        except Exception as e:
                            flash(f'OCR extraction failed: {str(e)}', 'error')
                            if filepath and os.path.exists(filepath):
                                try:
                                    os.remove(filepath)
                                except:
                                    pass
                            return redirect(request.url)
                    
                    # Clean up uploaded file
                    if filepath and os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except:
                            pass
            
            # Start with extracted parameters only (no default merging across diseases)
            # Each disease will use its own defaults in run_all_disease_models
            all_params = extracted_params.copy()
            
            # Override with manual entry (if provided)
            manual_fields = ['age', 'glucose', 'blood_pressure', 'bmi', 'chol', 'trestbps', 'thalach']
            for field in manual_fields:
                value = request.form.get(field)
                if value and value.strip():
                    try:
                        all_params[field] = float(value)
                        # Map aliases for consistency
                        if field == 'blood_pressure':
                            all_params['trestbps'] = float(value)
                        elif field == 'trestbps':
                            all_params['blood_pressure'] = float(value)
                    except ValueError:
                        pass
            
            # Get report history for trend analysis
            history = get_report_history_stack()
            trends = analyze_trends(all_params, history)
            
            # Run all disease models
            results = run_all_disease_models(all_params, all_symptoms)
            
            if not results:
                flash('No models available. Please train models first.', 'error')
                return redirect(request.url)
            
            # Rank results by priority
            ranked_results = rank_results_by_priority(results, trends)
            
            # Update trend information in results
            for result in ranked_results:
                # Check if trends indicate worsening
                for param_name, trend_data in trends.items():
                    if trend_data['trend'] == 'increasing':
                        result['trend_worsening'] = True
                        break
            
            # Save current report to history
            report_data = {
                'parameters': all_params.copy(),
                'symptoms': all_symptoms,
                'results': [{
                    'disease': r['disease_type'],
                    'prediction': r['prediction'],
                    'risk_score': r['risk_score']
                } for r in ranked_results]
            }
            save_report_to_history(report_data)
            
            # Render comprehensive results
            return render_template('comprehensive_result.html',
                                 results=ranked_results,
                                 trends=trends,
                                 symptoms=all_symptoms,
                                 parameters=all_params,
                                 history_count=len(history))
            
        except Exception as e:
            flash(f'Analysis failed: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET request - show upload form
    return render_template('general_analysis.html')

