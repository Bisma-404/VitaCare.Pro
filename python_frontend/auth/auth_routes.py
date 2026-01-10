"""
Authentication routes for staff and patient login.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import DatabaseConnection
from database.models import UserDAO, LoginHistoryDAO

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both staff and patients."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'patient')  # 'patient' or 'staff'
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return redirect(request.url)
        
        # Verify user credentials
        user = UserDAO.verify_password(username, password)
        
        if not user:
            flash('Invalid username or password', 'error')
            # Skip logging failed login attempt (user_id is required in schema)
            return redirect(request.url)
        
        # Check user type
        if user_type == 'staff' and user['role'] == 'PATIENT':
            flash('Staff login required for this account', 'error')
            return redirect(request.url)
        
        if user_type == 'patient' and user['role'] != 'PATIENT':
            flash('Patient login required for this account', 'error')
            return redirect(request.url)
        
        # Check if user is active
        if user['status'] != 'ACTIVE':
            flash('Your account is not active. Please contact administrator.', 'error')
            return redirect(request.url)
        
        # Store user in session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['name'] = user['name']
        session['user_type'] = user_type
        
        # Log successful login
        LoginHistoryDAO.create_login_record(
            user['id'],
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            success=True
        )
        
        # Redirect based on user type
        if user['role'] == 'ADMIN':
            flash(f'Welcome Admin, {user["name"]}!', 'success')
            return redirect(url_for('admin.dashboard'))
        elif user_type == 'staff':
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('staff.dashboard'))
        else:
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('patient.dashboard'))
    
    # GET request - show login form
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Logout user and clear session."""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Validation
        if not all([username, password, name]):
            flash('Please fill all required fields', 'error')
            return redirect(request.url)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(request.url)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(request.url)
        
        # Check if username already exists
        existing_user = UserDAO.get_user_by_username(username)
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(request.url)
        
        # Create patient user
        user_id = UserDAO.create_user(
            username=username,
            password=password,
            role='PATIENT',
            name=name,
            phone=phone,
            email=email,
            status='ACTIVE'
        )
        
        if user_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'error')
            return redirect(request.url)
    
    # GET request - show registration form
    return render_template('auth/register.html')

