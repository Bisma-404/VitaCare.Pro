"""
Main Flask application for VitaCare Pro - Multi-Disease Detection System.
Integrates MySQL database, DSA engine, and ML models.
"""

from flask import Flask, redirect, url_for, session
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.db_connection import init_db, DatabaseConnection
from auth.auth_routes import auth_bp
from staff.staff_routes import staff_bp
from patient.patient_routes import patient_bp

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = 'hospital-management-secret-key-change-in-production'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(patient_bp)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'hospital_management_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'abcd1234'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'pool_name': 'hospital_pool',
    'pool_size': 10,
    'pool_reset_session': True,
    'autocommit': False
}


@app.route('/')
def index():
    """Redirect to login page."""
    if 'user_id' in session:
        if session.get('user_type') == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))
    return redirect(url_for('auth.login'))


def initialize_database():
    """Initialize database connection on first request."""
    try:
        init_db(DB_CONFIG)
        print("✅ Database connection initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("Please ensure MySQL is running and database is created.")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 VitaCare Pro - Multi-Disease Detection System")
    print("="*60)
    
    # Test database connection
    try:
        init_db(DB_CONFIG)
        if DatabaseConnection.test_connection():
            print("✅ Database connection successful")
        else:
            print("⚠️  Database connection test failed")
    except Exception as e:
        print(f"⚠️  Database connection error: {e}")
        print("Please ensure MySQL is running and credentials are correct.")
    
    print("\n" + "="*60)
    print("Server starting at http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

