"""
Routes for the webapp portion of the application.
Handles disease detection portal and prediction logic.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import sys
import os
from werkzeug.utils import secure_filename
from ocr_utils import OCRParser
import re
from utils.medical_mappings import normalize_parameter_name

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.mapping import DISEASE_CONFIG
from predictions.prediction_engine import PredictionEngine

# Initialize Blueprint and Engine
webapp_bp = Blueprint('webapp', __name__)
prediction_engine = PredictionEngine()

# Initialize OCR parser
ocr_parser = OCRParser()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@webapp_bp.route('/portal')
def portal():
    """
    Render the main portal page (index.html from webapp).
    Injects disease configuration with icons for the template.
    """
    # Inject icons into config for the template
    diseases = DISEASE_CONFIG.copy()
    if 'diabetes' in diseases:
        diseases['diabetes']['icon'] = '🩸'
    if 'heart' in diseases:
        diseases['heart']['icon'] = '❤️'
    if 'breast_cancer' in diseases:
        diseases['breast_cancer']['icon'] = '🎗️'
        
    return render_template('index.html', diseases=diseases)

@webapp_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@webapp_bp.route('/predict/<disease_type>/ocr', methods=['GET', 'POST'])
def ocr_upload(disease_type):
    """
    Handle OCR upload for specific disease.
    """
    if disease_type not in DISEASE_CONFIG:
        flash('Invalid disease type', 'error')
        return redirect(url_for('webapp.portal'))
    
    config = DISEASE_CONFIG[disease_type]
    
    if request.method == 'POST':
        if 'ocr_image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        file = request.files['ocr_image']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            try:
                # Extract text
                text = ocr_parser.extract_text(filepath)
                
                # Extract parameters
                extracted_data = {}
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
                                
                                if normalized not in extracted_data:
                                    extracted_data[normalized] = value
                            except ValueError:
                                continue
                
                # Clean up
                os.remove(filepath)
                
                if not extracted_data:
                    flash('No relevant data found in image. Please enter manually.', 'warning')
                else:
                    flash('Data extracted successfully! Please review and confirm.', 'success')
                
                # Render form with extracted data
                return render_template('form.html', 
                                     disease=config, 
                                     form_data=extracted_data)
                                     
            except Exception as e:
                flash(f'OCR failed: {str(e)}', 'error')
                return redirect(request.url)
                
    return render_template('ocr_upload.html', 
                         disease_name=config['name'], 
                         disease_type=disease_type)

@webapp_bp.route('/predict/<disease_type>', methods=['GET', 'POST'])
def predict(disease_type):
    """
    Handle disease prediction.
    GET: Render the input form.
    POST: Process form data and show results.
    """
    if disease_type not in DISEASE_CONFIG:
        flash('Invalid disease type', 'error')
        return redirect(url_for('webapp.portal'))
    
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
                    test_data[field_name] = float(value)
            
            # Get symptoms (optional, for now empty list if not provided)
            symptoms = [] 
            
            # Run prediction
            result = prediction_engine.predict(test_data, symptoms, disease_type)
            
            # Render result
            return render_template('result.html', 
                                 result=result, 
                                 disease=config,
                                 form_data=form_data)
                                 
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            return redirect(request.url)
            
    # GET request
    return render_template('form.html', disease=config)
