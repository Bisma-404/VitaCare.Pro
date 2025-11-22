"""
Flask web application for disease prediction.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sys
import os
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.mapping import get_disease_config, extract_features_from_form
from ocr_utils import OCRParser, get_default_values

# Import C++ tree module
try:
    import cpp_tree
except ImportError:
    print("Warning: cpp_tree module not found. Please ensure it's in the Python path.")
    cpp_tree = None

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# OCR Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OCR parser
ocr_parser = OCRParser()

# Global model storage
models = {}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_model(disease_type):
    """Load a trained model from disk using C++ DecisionTree .load(). Prints debug info!"""
    if disease_type in models:
        return models[disease_type]
    
    # Use absolute path based on script location, not working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get webapp directory
    models_dir = os.path.join(script_dir, '..', 'models')     # Go up one level to python_frontend, then models
    model_path = os.path.join(models_dir, f'{disease_type}_model.txt')
    
    # Normalize the path to resolve .. properly
    model_path = os.path.normpath(model_path)
    
    print(f"[DEBUG] Attempting to load model for '{disease_type}' from {model_path}")
    
    if not os.path.exists(model_path):
        print(f"[ERROR] Model file does not exist: {model_path}")
        return None
    
    try:
        model = cpp_tree.DecisionTree()
        loaded = model.load(model_path)
        print(f"[DEBUG] cpp_tree.DecisionTree.load returned: {loaded}")
        if not loaded:
            print(f"[ERROR] C++ model load failed for: {model_path}")
            return None
        models[disease_type] = model
        return model
    except Exception as e:
        print(f"Error loading model ({model_path}): {e}")
        return None


def get_remarks(disease_type, prediction, features):
    if disease_type == 'diabetes':
        glucose = features[1] if len(features) > 1 else 0
        bmi = features[5] if len(features) > 5 else 0
        if prediction == 1:
            if glucose > 170:
                return 'High diabetes risk and very elevated glucose! Please consult a doctor immediately.'
            elif bmi > 32:
                return 'High risk and high BMI detected. Talk with your doctor about weight management.'
            else:
                return 'High risk detected. Please consult a doctor soon for further assessment.'
        else:
            if glucose < 100:
                return 'No diabetes risk and healthy glucose. Keep it up!'
            else:
                return 'No diabetes risk detected. Maintain a healthy lifestyle!'
    elif disease_type == 'heart':
        age = features[0] if len(features) > 0 else 0
        chol = features[4] if len(features) > 4 else 0
        if prediction == 1:
            if age > 60:
                return 'No heart disease, but your age suggests regular cardiac checkups.'
            else:
                return 'No heart disease detected. Keep a healthy routine.'
        else:
            if age > 60:
                return 'AT RISK: Cardiac danger in advanced age. Schedule a cardiology checkup!'
            elif chol > 240:
                return 'Warning: High cholesterol and cardiac risk detected. Seek medical attention promptly.'
            else:
                return 'Urgent: cardiac risk detected! Schedule a medical appointment now.'
    elif disease_type == 'breast_cancer':
        radius_mean = features[0] if len(features) > 0 else 0
        if prediction == 1:
            if radius_mean > 15:
                return 'Warning: Malignant, large suspicious mass detected. Urgent oncologist referral needed.'
            else:
                return 'Warning: suspicious malignant features detected. Please see your oncologist as soon as possible.'
        else:
            return 'Benign result. Routine screenings and vigilance are still recommended.'
    return "Result interpretation is unavailable."
@app.route('/')
def index():
    """Home page with disease selection."""
    diseases = {
        'diabetes': {
            'name': 'Diabetes',
            'description': 'Predict diabetes risk based on medical indicators',
            'icon': '🩺'
        },
        'heart': {
            'name': 'Heart Disease',
            'description': 'Assess cardiovascular health and disease risk',
            'icon': '❤️'
        },
        'breast_cancer': {
            'name': 'Breast Cancer',
            'description': 'Analyze cell characteristics for malignancy detection',
            'icon': '🎗️'
        }
    }
    return render_template('index.html', diseases=diseases)


@app.route('/predict/<disease_type>', methods=['GET', 'POST'])
def predict(disease_type):
    """Disease prediction form and result."""
    config = get_disease_config(disease_type)
    
    if not config:
        flash('Invalid disease type', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Extract features from form
            features = extract_features_from_form(request.form, disease_type)
            
            # Load model
            model = load_model(disease_type)
            if model is None:
                flash(f'Model not found for {disease_type}. Please train the model first.', 'error')
                return redirect(url_for('predict', disease_type=disease_type))
            
            # Make prediction
            prediction = model.predict(features)
            outcome_label = config['outcome_labels'].get(prediction, 'Unknown')
            
            return render_template('result.html',
                                 disease_name=config['name'],
                                 prediction=prediction,
                                 outcome=outcome_label,
                                 features=features,
                                 field_names=[f['label'] for f in config['fields']],
                                 remark=get_remarks(disease_type, prediction, features))
            
        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'error')
            return redirect(url_for('predict', disease_type=disease_type))
    
    # GET request - show form
    return render_template('form.html',
                         disease_type=disease_type,
                         disease_name=config['name'],
                         description=config['description'],
                         fields=config['fields'])

@app.route('/ocr-upload/<disease_type>', methods=['GET', 'POST'])
def ocr_upload(disease_type):
    """Handle OCR image upload and extraction."""
    config = get_disease_config(disease_type)
    
    if not config:
        flash('Invalid disease type', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'ocr_image' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['ocr_image']
        
        # Check if file is empty
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Validate file type
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload an image (JPG, PNG, BMP, TIFF)', 'error')
            return redirect(request.url)
        
        try:
            # Save file securely
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Perform OCR extraction
            result = ocr_parser.parse_report(filepath, disease_type)
            
            # Get default values for missing fields
            defaults = get_default_values(disease_type)
            parsed_data = result['parsed_data']
            
            # Merge parsed data with defaults
            complete_data = defaults.copy()
            complete_data.update(parsed_data)
            
            # Store in session for review page
            session['ocr_data'] = {
                'raw_text': result['raw_text'],
                'parsed_data': complete_data,
                'fields_found': result['fields_found'],
                'disease_type': disease_type,
                'filename': filename
            }
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
            
            # Redirect to review page
            return redirect(url_for('ocr_review', disease_type=disease_type))
            
        except Exception as e:
            flash(f'OCR processing failed: {str(e)}', 'error')
            # Clean up file if it exists
            if 'filepath' in locals() and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            return redirect(request.url)
    
    # GET request - show upload form
    return render_template('ocr_upload.html',
                         disease_type=disease_type,
                         disease_name=config['name'],
                         description=config['description'])


@app.route('/ocr-review/<disease_type>', methods=['GET', 'POST'])
def ocr_review(disease_type):
    """Review and edit OCR-extracted data before prediction."""
    config = get_disease_config(disease_type)
    
    if not config:
        flash('Invalid disease type', 'error')
        return redirect(url_for('index'))
    
    # Check if OCR data exists in session
    if 'ocr_data' not in session:
        flash('No OCR data found. Please upload an image first.', 'error')
        return redirect(url_for('ocr_upload', disease_type=disease_type))
    
    ocr_data = session['ocr_data']
    
    # Verify disease type matches
    if ocr_data['disease_type'] != disease_type:
        flash('Disease type mismatch', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Extract edited features from form
            features = extract_features_from_form(request.form, disease_type)
            
            # Load model
            model = load_model(disease_type)
            if model is None:
                flash(f'Model not found for {disease_type}. Please train the model first.', 'error')
                return redirect(url_for('ocr_upload', disease_type=disease_type))
            
            # Make prediction
            prediction = model.predict(features)
            outcome_label = config['outcome_labels'].get(prediction, 'Unknown')
            
            # Clear session data
            session.pop('ocr_data', None)
            
            return render_template('result.html',
                                 disease_name=config['name'],
                                 prediction=prediction,
                                 outcome=outcome_label,
                                 features=features,
                                 field_names=[f['label'] for f in config['fields']],
                                 remark=get_remarks(disease_type, prediction, features),
                                 from_ocr=True)
            
        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET request - show review form with extracted data
    return render_template('ocr_review.html',
                         disease_type=disease_type,
                         disease_name=config['name'],
                         description=config['description'],
                         fields=config['fields'],
                         ocr_data=ocr_data['parsed_data'],
                         raw_text=ocr_data['raw_text'],
                         fields_found=ocr_data['fields_found'])


@app.route('/about')
def about():
    """About page with system information."""
    return render_template('about.html')


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Multi-Disease Detection System - Starting Server")
    print("="*60)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.normpath(os.path.join(script_dir, '..', 'models'))
    if os.path.exists(models_dir):
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.txt')]
        if model_files:
            print(f"\nFound {len(model_files)} trained model(s):")
            for model_file in model_files:
                print(f"  ✓ {model_file}")
        else:
            print("\n⚠️  Warning: No trained models found!")
            print("Please train models first using train.py")
    else:
        print("\n⚠️  Warning: Models directory not found!")
        print("Please train models first using train.py")
    print("\n" + "="*60)
    print("Server starting at http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)