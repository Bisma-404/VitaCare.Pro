"""
Admin Routes - User and Symptom Management for Doctors & Lab Technicians
"""
import traceback
import json
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from database.db_connection import get_db_connection
from utils.password_hash import hash_password
import os
import csv
import re
from werkzeug.utils import secure_filename
from predictions.prediction_engine import PredictionEngine
from utils.mapping import DISEASE_CONFIG
from ocr_utils import OCRParser, get_default_values
from utils.medical_mappings import normalize_parameter_name
from utils.cpp_dsa_wrapper import MedicalHashMap

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
prediction_engine = PredictionEngine()
ocr_parser = OCRParser()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf', 'csv'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# ADMIN AUTHENTICATION MIDDLEWARE
# ============================================================================

def admin_required(f):
    """Decorator to ensure user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or user['role'] != 'ADMIN':
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM users WHERE role = 'DOCTOR') as doctor_count,
            (SELECT COUNT(*) FROM users WHERE role = 'LAB_TECH') as lab_tech_count,
            (SELECT COUNT(*) FROM users WHERE role = 'PATIENT') as patient_count,
            (SELECT COUNT(*) FROM patient_reports) as total_reports
    """)
    stats = cursor.fetchone()
    
    # Get recent users
    cursor.execute("""
        SELECT id, username, email, role, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_users = cursor.fetchall()
    
    # Get disease distribution from predictions
    cursor.execute("""
        SELECT dm.disease_name, COUNT(*) as count 
        FROM predictions p
        JOIN disease_models dm ON p.disease_id = dm.id
        GROUP BY dm.disease_name 
        ORDER BY count DESC 
        LIMIT 5
    """)
    disease_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         disease_stats=disease_stats)

# ============================================================================
# USER MANAGEMENT - DOCTOR/LAB TECH
# ============================================================================

@admin_bp.route('/users', methods=['GET'])
@admin_required
def manage_users():
    """List all users by role"""
    role = request.args.get('role', 'all')
    q = (request.args.get('q') or '').strip()
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        page_size = int(request.args.get('page_size', 10))
    except ValueError:
        page_size = 10

    offset = max(0, (page - 1)) * max(1, page_size)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    base_where = []
    params = []

    # Role filter
    if role != 'all':
        role_upper = role.upper()
        # Normalize accepted role names
        if role_upper not in ('DOCTOR', 'LAB_TECH', 'PATIENT', 'ADMIN'):
            role_upper = 'PATIENT'
        base_where.append('role = %s')
        params.append(role_upper)

    # Text search
    if q:
        like_q = f"%{q}%"
        base_where.append('(username LIKE %s OR email LIKE %s OR phone LIKE %s)')
        params.extend([like_q, like_q, like_q])

    where_clause = ('WHERE ' + ' AND '.join(base_where)) if base_where else ''

    # Total count for pagination
    count_query = f"SELECT COUNT(*) as total FROM users {where_clause}"
    cursor.execute(count_query, tuple(params) if params else None)
    total_count = cursor.fetchone().get('total', 0)
    total_pages = max(1, (total_count + max(1, page_size) - 1) // max(1, page_size))

    # Fetch page
    query = f"""
        SELECT id, username, email, role, created_at, phone
        FROM users
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    exec_params = list(params) if params else []
    exec_params.extend([page_size, offset])

    cursor.execute(query, tuple(exec_params))
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/manage_users.html', users=users, current_role=role,
                           q=q, page=page, page_size=page_size, total_pages=total_pages, total_count=total_count)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add new doctor or lab technician"""
    if request.method == 'GET':
        return render_template('admin/add_user.html')
    
    # POST request - add user
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  # 'doctor' or 'lab_tech'
    name = data.get('name', username)  # Use username as default if name not provided
    phone_number = data.get('phone_number', '')
    
    # Validation
    if not all([username, email, password, role]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Map role to uppercase ENUM
    role_mapping = {
        'doctor': 'DOCTOR',
        'lab_tech': 'LAB_TECH',
        'patient': 'PATIENT'
    }
    
    if role not in role_mapping:
        return jsonify({'error': 'Invalid role'}), 400
    
    role_enum = role_mapping[role]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Email or username already registered'}), 409
        
        # Hash password using the project's double-hash scheme
        salt, digest = hash_password(password, rounds=1000)
        password_hash = f"{salt}${digest}"
        
        # Insert user - need name field, use provided name or username as default
        cursor.execute("""
            INSERT INTO users 
            (username, email, password, role, phone, name, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
        """, (username, email, password_hash, role_enum, phone_number, name))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': f'{role.title()} added successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user information"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'GET':
        cursor.execute("""
            SELECT id, username, email, role, phone, name
            FROM users
            WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return render_template('admin/edit_user.html', user=user)
    
    # POST request - update user
    data = request.get_json()
    role = data.get('role')
    phone_number = data.get('phone_number', '')
    name = data.get('name', '')
    
    # Map role to uppercase ENUM
    role_mapping = {
        'doctor': 'DOCTOR',
        'lab_tech': 'LAB_TECH',
        'patient': 'PATIENT',
        'admin': 'ADMIN'
    }
    
    if role and role not in role_mapping:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Invalid role'}), 400
    
    try:
        updates = []
        params = []
        
        if role:
            updates.append("role = %s")
            params.append(role_mapping[role])
        if phone_number:
            updates.append("phone = %s")
            params.append(phone_number)
        if name:
            updates.append("name = %s")
            params.append(name)
        
        if not updates:
            cursor.close()
            conn.close()
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(user_id)
        cursor.execute(f"""
            UPDATE users
            SET {', '.join(updates)}, last_updated = NOW()
            WHERE id = %s
        """, tuple(params))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'User updated successfully'}), 200
    
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Don't allow deleting admin
        cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        if user['role'] == 'ADMIN':
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cannot delete admin users'}), 403
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SYMPTOM MANAGEMENT - Using DSA
# ============================================================================

@admin_bp.route('/symptoms', methods=['GET'])
@admin_required
def manage_symptoms():
    """List all symptoms with analytics"""
    try:
        from cpp_tree import SymptomManager

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get all unique symptoms from database with disease category
        cursor.execute("""
            SELECT symptom_name, disease_category, description FROM symptoms
            ORDER BY symptom_name ASC
        """)
        symptoms = cursor.fetchall()

        # Initialize DSA SymptomManager (safe)
        # Extract symptom names for DSA
        symptom_names = [s['symptom_name'] for s in symptoms]
        
        symptom_manager = None
        symptom_count = 0
        try:
            symptom_manager = SymptomManager()
            # load_symptoms may be heavy or fail if cpp_tree not compiled; guard it
            symptom_manager.load_symptoms(symptom_names)
            symptom_count = getattr(symptom_manager, 'get_symptom_count', lambda: len(symptom_names))()
        except Exception as inner_e:
            # Log and continue - show partial page with message
            print(f"SymptomManager load failed: {inner_e}")
            symptom_manager = None
            symptom_count = len(symptom_names)

        # Get frequency analytics - join with symptoms table to get symptom_name
        cursor.execute("""
            SELECT s.symptom_name, COUNT(*) as frequency
            FROM patient_symptoms ps
            JOIN symptoms s ON ps.symptom_id = s.id
            GROUP BY s.symptom_name
            ORDER BY frequency DESC
            LIMIT 20
        """)
        frequency_stats = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('admin/manage_symptoms.html',
                             symptoms=symptoms,
                             symptom_count=symptom_count,
                             frequency_stats=frequency_stats,
                             dsa_error=None)
    
    except Exception as e:
        # Provide useful error to template while avoiding crash
        print(f"manage_symptoms error: {e}")
        return render_template('admin/manage_symptoms.html',
                             error=str(e),
                             symptoms=[],
                             symptom_count=0,
                             frequency_stats=[],
                             dsa_error=str(e))

@admin_bp.route('/symptoms/add', methods=['POST'])
@admin_required
def add_symptom():
    """Add new symptom with disease category"""
    data = request.get_json()
    symptom_name = data.get('symptom_name', '').strip()
    disease_category = data.get('disease_category', '').strip()
    description = data.get('description', '').strip()
    
    if not symptom_name:
        return jsonify({'error': 'Symptom name required'}), 400
    
    if not disease_category:
        return jsonify({'error': 'Disease category required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if symptom exists
        cursor.execute("SELECT id FROM symptoms WHERE symptom_name = %s", (symptom_name,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Symptom already exists'}), 409
        
        # Add symptom with disease category
        cursor.execute("""
            INSERT INTO symptoms (symptom_name, disease_category, description)
            VALUES (%s, %s, %s)
        """, (symptom_name, disease_category, description))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Symptom added successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/symptoms/get-id', methods=['GET'])
@admin_required
def get_symptom_id():
    """Get symptom ID by name"""
    symptom_name = request.args.get('name')
    if not symptom_name:
        return jsonify({'error': 'Symptom name required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM symptoms WHERE symptom_name = %s", (symptom_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return jsonify({'id': result['id']}), 200
        else:
            return jsonify({'error': 'Symptom not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/symptoms/<int:symptom_id>/delete', methods=['DELETE'])
@admin_required
def delete_symptom(symptom_id):
    """Delete a symptom"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM symptoms WHERE id = %s", (symptom_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Symptom deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/symptoms/search', methods=['GET'])
@admin_required
def search_symptoms():
    """Search symptoms by prefix using DSA"""
    try:
        from cpp_tree import SymptomManager
        
        prefix = request.args.get('q', '').strip()
        
        if not prefix:
            return jsonify({'results': []}), 200
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all symptoms
        cursor.execute("""
            SELECT DISTINCT symptom_name FROM symptoms
            ORDER BY symptom_name ASC
        """)
        symptoms = [row['symptom_name'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        # Use DSA binary search with prefix matching
        symptom_manager = SymptomManager()
        symptom_manager.load_symptoms(symptoms)
        results = symptom_manager.search_by_prefix(prefix)
        
        return jsonify({'results': results}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def analytics():
    """Admin analytics dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Disease distribution - get from predictions table
    cursor.execute("""
        SELECT dm.disease_name, COUNT(*) as count 
        FROM predictions p
        JOIN disease_models dm ON p.disease_id = dm.id
        GROUP BY dm.disease_name 
        ORDER BY count DESC
    """)
    disease_distribution = cursor.fetchall()
    
    # Risk level distribution - based on prediction_result (0=Low Risk, 1=High Risk)
    cursor.execute("""
        SELECT 
            CASE 
                WHEN prediction_result = 1 THEN 'HIGH_RISK'
                ELSE 'LOW_RISK'
            END as risk_level,
            COUNT(*) as count
        FROM predictions
        GROUP BY prediction_result
    """)
    risk_distribution = cursor.fetchall()
    
    # Predictions by staff - join with users table
    cursor.execute("""
        SELECT u.username, COUNT(*) as prediction_count
        FROM predictions p
        JOIN patient_reports pr ON p.report_id = pr.id
        JOIN users u ON pr.staff_id = u.id
        GROUP BY pr.staff_id, u.username
        ORDER BY prediction_count DESC
    """)
    staff_predictions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/analytics.html',
                         disease_distribution=disease_distribution,
                         risk_distribution=risk_distribution,
                         staff_predictions=staff_predictions)

# ============================================================================
# DISEASE DETECTION (Admin)
# ============================================================================

@admin_bp.route('/disease-detection', methods=['GET'])
@admin_required
def disease_selection():
    """Render disease selection page for Admin."""
    return render_template('admin/disease_selection.html')

@admin_bp.route('/predict/<disease_type>', methods=['GET', 'POST'])
@admin_required
def predict_disease(disease_type):
    """
    Handle disease prediction for Admin.
    GET: Render the input form.
    POST: Process form data and show results.
    """
    if disease_type not in DISEASE_CONFIG:
        flash('Invalid disease type', 'error')
        return redirect(url_for('admin.disease_selection'))
    
    config = DISEASE_CONFIG[disease_type]
    
    if request.method == 'POST':
        print(f"[DEBUG] POST request received for disease_type: {disease_type}")
        try:
            test_data = {}
            file_uploaded = False
            
            # Check if file was uploaded (OCR mode)
            if 'report_file' in request.files:
                file = request.files['report_file']
                print(f"[DEBUG] report_file found. Filename: '{file.filename}'")
                # Only process file if it has a filename (user actually selected a file)
                if file and file.filename and file.filename.strip() and allowed_file(file.filename):
                    file_uploaded = True
                    print(f"[DEBUG] File uploaded: {file.filename}")
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
                    print(f"[DEBUG] Redirecting to OCR review with data: {test_data}")
                    return redirect(url_for('admin.ocr_review', disease_type=disease_type))
            
            print(f"[DEBUG] file_uploaded={file_uploaded}, test_data keys: {list(test_data.keys())}")
            
            # If no file uploaded or manual input mode, extract from form
            if not file_uploaded or not test_data:
                print(f"[DEBUG] Extracting from manual form input")
                form_data = request.form.to_dict()
                print(f"[DEBUG] Form data keys: {list(form_data.keys())}")
                for field in config['fields']:
                    field_name = field['name']
                    value = form_data.get(field_name)
                    if value:
                        try:
                            test_data[field_name] = float(value)
                        except ValueError:
                            continue
            
            print(f"[DEBUG] Final test_data: {test_data}")
            
            # Fill missing fields with defaults from OCR data
            if test_data:
                for field in config['fields']:
                    field_name = field['name']
                    if field_name not in test_data:
                        normalized = normalize_parameter_name(field_name)
                        if normalized in test_data:
                            test_data[field_name] = test_data[normalized]
                        else:
                            test_data[field_name] = field.get('default', 0)
            
            # Get symptoms (optional)
            symptoms_text = request.form.get('symptoms_text', '')
            symptoms = [s.strip() for s in symptoms_text.split(',') if s.strip()] 
            
            print(f"[DEBUG] Running prediction with test_data: {test_data}")
            # Run prediction
            result = prediction_engine.predict(test_data, symptoms, disease_type)
            
            print(f"[DEBUG] Prediction result: {result}")
            
            # Build features list in correct order matching config fields
            features = []
            for field in config['fields']:
                features.append(test_data.get(field['name'], field.get('default', 0)))

            # Persist prediction to database (minimal flow)
            try:
                from database.models import PredictionDAO, PatientReportDAO

                # Resolve disease_id by slug if available
                disease_id = None
                try:
                    conn = get_db_connection()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT id FROM disease_models WHERE disease_name = %s OR disease_code = %s", (disease_type, disease_type))
                    r = cur.fetchone()
                    if r:
                        disease_id = r.get('id')
                    cur.close()
                    conn.close()
                except Exception:
                    traceback.print_exc()

                report_id = None
                # If the admin provided a patient_id in the form, create a report and attach the prediction
                patient_id = request.form.get('patient_id') or request.form.get('patient')
                if patient_id:
                    try:
                        staff_id = session.get('user_id')
                        # Use 'GENERAL' report_type to match DB enum/length constraints
                        report_id = PatientReportDAO.create_report(int(patient_id), staff_id, 'GENERAL', uploaded_file=None, notes='Admin prediction via UI')
                        if not report_id:
                            print('Warning: PatientReportDAO.create_report returned None')
                    except Exception:
                        traceback.print_exc()

                # Create prediction record (report_id may be None)
                try:
                    if report_id is not None and disease_id is not None:
                        PredictionDAO.create_prediction(report_id, disease_id, int(result.get('prediction', 0)), float(result.get('confidence', 0)), method=result.get('method', 'DSA'))
                    else:
                        print('Skipping PredictionDAO.create_prediction because report_id or disease_id is None')
                except Exception:
                    traceback.print_exc()
            except Exception:
                traceback.print_exc()

            # Prepare metrics for template (fallback to dsa_result when ML replaced top-level keys)
            dsa_sub = result.get('dsa_result', {})
            template_thresholds = result.get('threshold_violations', dsa_sub.get('threshold_violations', []))
            template_symptoms = result.get('symptom_matches', dsa_sub.get('symptom_matches', 0))
            template_risk = result.get('risk_score', dsa_sub.get('risk_score', 0))
            template_severity = result.get('severity_label', dsa_sub.get('severity_label', None))
            template_severity_reason = result.get('severity_reason', dsa_sub.get('severity_reason', ''))

            # Render result page (full page response)
            return render_template('admin/predict_result.html', 
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
            print(f"[ERROR] Prediction failed: {str(e)}")
            traceback.print_exc()
            flash(f'Prediction failed: {str(e)}', 'error')
            return redirect(request.url)
            
            
    # GET request
    return render_template('admin/predict_form.html', 
                         disease_name=config['name'],
                         fields=config['fields'],
                         disease_type=disease_type)


@admin_bp.route('/predict/<disease_type>/ocr-review', methods=['GET', 'POST'])
@admin_required
def ocr_review(disease_type):
    """
    OCR Review Page - Display extracted data for user verification.
    GET: Show review form with extracted data.
    POST: Process reviewed data and run prediction.
    """
    if disease_type not in DISEASE_CONFIG:
        flash('Invalid disease type', 'error')
        return redirect(url_for('admin.disease_selection'))
    
    config = DISEASE_CONFIG[disease_type]
    
    # Get extracted data from session
    extracted_data = session.get('ocr_extracted_data', {})
    stored_disease_type = session.get('disease_type_for_review')
    
    # Verify disease type matches
    if stored_disease_type != disease_type:
        flash('Session mismatch. Please upload the file again.', 'error')
        return redirect(url_for('admin.predict_disease', disease_type=disease_type))
    
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
        
        # Clear session data
        session.pop('ocr_extracted_data', None)
        session.pop('disease_type_for_review', None)
        
        # Run prediction
        try:
            symptoms = []  # Optional
            result = prediction_engine.predict(test_data, symptoms, disease_type)
            
            # Build features list in correct order matching config fields
            features = []
            for field in config['fields']:
                features.append(test_data.get(field['name'], field.get('default', 0)))
            
            # Render result
            # Persist prediction (OCR review flow)
            try:
                from database.models import PredictionDAO, PatientReportDAO

                disease_id = None
                try:
                    conn = get_db_connection()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT id FROM disease_models WHERE disease_name = %s OR disease_code = %s", (disease_type, disease_type))
                    rr = cur.fetchone()
                    if rr:
                        disease_id = rr.get('id')
                    cur.close()
                    conn.close()
                except Exception:
                    traceback.print_exc()

                report_id = None
                patient_id = request.form.get('patient_id') or request.form.get('patient')
                if patient_id:
                    try:
                        staff_id = session.get('user_id')
                        # Use 'GENERAL' report_type to match DB enum/length constraints
                        report_id = PatientReportDAO.create_report(int(patient_id), staff_id, 'GENERAL', uploaded_file=None, notes='OCR-reviewed prediction via UI')
                        if not report_id:
                            print('Warning: PatientReportDAO.create_report returned None')
                    except Exception:
                        traceback.print_exc()

                try:
                    if report_id is not None:
                        PredictionDAO.create_prediction(report_id, disease_id, int(result.get('prediction', 0)), float(result.get('confidence', 0)), method=result.get('method', 'DSA'))
                    else:
                        print('Skipping PredictionDAO.create_prediction because report_id is None')
                except Exception:
                    traceback.print_exc()
            except Exception:
                traceback.print_exc()

            return render_template('admin/predict_result.html', 
                                 prediction=result['prediction'],
                                 outcome=config['outcome_labels'][result['prediction']],
                                 remark=result.get('remark', 'Based on the analysis of provided health metrics.'),
                                 features=features,
                                 field_names=[f['label'] for f in config['fields']],
                                 disease_name=config['name'],
                                 disease_type=disease_type)
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            return redirect(url_for('admin.predict_disease', disease_type=disease_type))
    
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
    
    return render_template('admin/ocr_review.html',
                         disease_name=config['name'],
                         disease_type=disease_type,
                         fields=fields_with_values,
                         auto_filled_count=auto_filled_count,
                         default_count=default_count,
                         total_count=len(fields_with_values))

