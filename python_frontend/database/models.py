"""
Database models/DAOs for hospital management system.
Data Access Objects for interacting with MySQL database.
"""

from database.db_connection import DatabaseConnection
from mysql.connector import Error
import hashlib
from datetime import datetime


class UserDAO:
    """Data Access Object for users table."""
    
    @staticmethod
    def create_user(username, password, role, name, phone=None, email=None, status='ACTIVE'):
        """Create a new user."""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
            INSERT INTO users (username, password, role, name, phone, email, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            user_id = DatabaseConnection.execute_query(
                query,
                (username, hashed_password, role, name, phone, email, status),
                fetch=False
            )
            return user_id
        except Error as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username."""
        query = "SELECT * FROM users WHERE username = %s"
        result = DatabaseConnection.execute_query(query, (username,))
        return result[0] if result else None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        query = "SELECT * FROM users WHERE id = %s"
        result = DatabaseConnection.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def verify_password(username, password):
        """Verify user password."""
        user = UserDAO.get_user_by_username(username)
        if not user:
            return None
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] == hashed_password:
            return user
        return None
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user information."""
        allowed_fields = ['name', 'phone', 'email', 'status']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)}, last_updated = NOW() WHERE id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(params), fetch=False)
            return True
        except Error as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def get_all_staff():
        """Get all staff users."""
        query = "SELECT * FROM users WHERE role IN ('ADMIN', 'DOCTOR', 'LAB_TECH') ORDER BY name"
        return DatabaseConnection.execute_query(query)
    
    @staticmethod
    def get_all_patients():
        """Get all patients."""
        query = "SELECT * FROM users WHERE role = 'PATIENT' ORDER BY name"
        return DatabaseConnection.execute_query(query)


class PatientProfileDAO:
    """Data Access Object for patient_profiles table."""
    
    @staticmethod
    def create_profile(patient_id, date_of_birth, gender, blood_group=None, address=None):
        """Create patient profile."""
        query = """
            INSERT INTO patient_profiles (patient_id, date_of_birth, gender, blood_group, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            profile_id = DatabaseConnection.execute_query(
                query,
                (patient_id, date_of_birth, gender, blood_group, address),
                fetch=False
            )
            return profile_id
        except Error as e:
            print(f"Error creating profile: {e}")
            return None
    
    @staticmethod
    def get_profile_by_patient_id(patient_id):
        """Get profile by patient ID."""
        query = """
            SELECT pp.*, u.name, u.email, u.phone
            FROM patient_profiles pp
            JOIN users u ON pp.patient_id = u.id
            WHERE pp.patient_id = %s
        """
        result = DatabaseConnection.execute_query(query, (patient_id,))
        return result[0] if result else None
    
    @staticmethod
    def update_profile(patient_id, **kwargs):
        """Update patient profile."""
        allowed_fields = ['date_of_birth', 'gender', 'blood_group', 'address', 'emergency_contact']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(patient_id)
        query = f"UPDATE patient_profiles SET {', '.join(updates)}, updated_at = NOW() WHERE patient_id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(params), fetch=False)
            return True
        except Error as e:
            print(f"Error updating profile: {e}")
            return False


class PatientReportDAO:
    """Data Access Object for patient_reports table."""
    
    @staticmethod
    def create_report(patient_id, staff_id, report_type, uploaded_file=None, notes=None):
        """Create a new patient report."""
        query = """
            INSERT INTO patient_reports (patient_id, staff_id, report_type, uploaded_file, notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            report_id = DatabaseConnection.execute_query(
                query,
                (patient_id, staff_id, report_type, uploaded_file, notes),
                fetch=False
            )
            return report_id
        except Error as e:
            print(f"Error creating report: {e}")
            return None
    
    @staticmethod
    def get_report_by_id(report_id):
        """Get report by ID."""
        query = """
            SELECT pr.*, u.name as patient_name, s.name as staff_name
            FROM patient_reports pr
            JOIN users u ON pr.patient_id = u.id
            JOIN users s ON pr.staff_id = s.id
            WHERE pr.id = %s
        """
        result = DatabaseConnection.execute_query(query, (report_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_reports_by_patient(patient_id):
        """Get all reports for a patient."""
        query = """
            SELECT pr.*, s.name as staff_name
            FROM patient_reports pr
            JOIN users s ON pr.staff_id = s.id
            WHERE pr.patient_id = %s
            ORDER BY pr.created_at DESC
        """
        return DatabaseConnection.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_all_reports():
        """Get all reports."""
        query = """
            SELECT pr.*, u.name as patient_name, s.name as staff_name
            FROM patient_reports pr
            JOIN users u ON pr.patient_id = u.id
            JOIN users s ON pr.staff_id = s.id
            ORDER BY pr.created_at DESC
        """
        return DatabaseConnection.execute_query(query)
    
    @staticmethod
    def update_report(report_id, **kwargs):
        """Update report."""
        allowed_fields = ['report_type', 'uploaded_file', 'notes', 'status']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(report_id)
        query = f"UPDATE patient_reports SET {', '.join(updates)}, updated_at = NOW() WHERE id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(params), fetch=False)
            return True
        except Error as e:
            print(f"Error updating report: {e}")
            return False
    
    @staticmethod
    def delete_report(report_id):
        """Delete a report."""
        query = "DELETE FROM patient_reports WHERE id = %s"
        try:
            DatabaseConnection.execute_query(query, (report_id,), fetch=False)
            return True
        except Error as e:
            print(f"Error deleting report: {e}")
            return False


class ReportTestDAO:
    """Data Access Object for report_tests table."""
    
    @staticmethod
    def create_test(report_id, test_name, test_value, unit=None, normal_range=None):
        """Create a test result."""
        query = """
            INSERT INTO report_tests (report_id, test_name, test_value, unit, normal_range)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            test_id = DatabaseConnection.execute_query(
                query,
                (report_id, test_name, test_value, unit, normal_range),
                fetch=False
            )
            return test_id
        except Error as e:
            print(f"Error creating test: {e}")
            return None
    
    @staticmethod
    def get_tests_by_report(report_id):
        """Get all tests for a report."""
        query = "SELECT * FROM report_tests WHERE report_id = %s ORDER BY test_name"
        return DatabaseConnection.execute_query(query, (report_id,))
    
    @staticmethod
    def delete_tests_by_report(report_id):
        """Delete all tests for a report."""
        query = "DELETE FROM report_tests WHERE report_id = %s"
        try:
            DatabaseConnection.execute_query(query, (report_id,), fetch=False)
            return True
        except Error as e:
            print(f"Error deleting tests: {e}")
            return False


class DiseaseThresholdDAO:
    """Data Access Object for disease_thresholds table."""
    
    @staticmethod
    def create_threshold(disease_id, parameter_name, min_value, max_value, unit=None):
        """Create a disease threshold."""
        query = """
            INSERT INTO disease_thresholds (disease_id, parameter_name, min_value, max_value, unit)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            threshold_id = DatabaseConnection.execute_query(
                query,
                (disease_id, parameter_name, min_value, max_value, unit),
                fetch=False
            )
            return threshold_id
        except Error as e:
            print(f"Error creating threshold: {e}")
            return None
    
    @staticmethod
    def get_thresholds_by_disease(disease_id):
        """Get all thresholds for a disease."""
        query = "SELECT * FROM disease_thresholds WHERE disease_id = %s ORDER BY parameter_name"
        return DatabaseConnection.execute_query(query, (disease_id,))
    
    @staticmethod
    def get_all_thresholds():
        """Get all thresholds."""
        query = """
            SELECT dt.*, dm.disease_name
            FROM disease_thresholds dt
            JOIN disease_models dm ON dt.disease_id = dm.id
            ORDER BY dm.disease_name, dt.parameter_name
        """
        return DatabaseConnection.execute_query(query)
    
    @staticmethod
    def update_threshold(threshold_id, **kwargs):
        """Update threshold."""
        allowed_fields = ['parameter_name', 'min_value', 'max_value', 'unit']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(threshold_id)
        query = f"UPDATE disease_thresholds SET {', '.join(updates)} WHERE id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(params), fetch=False)
            return True
        except Error as e:
            print(f"Error updating threshold: {e}")
            return False
    
    @staticmethod
    def delete_threshold(threshold_id):
        """Delete a threshold."""
        query = "DELETE FROM disease_thresholds WHERE id = %s"
        try:
            DatabaseConnection.execute_query(query, (threshold_id,), fetch=False)
            return True
        except Error as e:
            print(f"Error deleting threshold: {e}")
            return False


class PredictionDAO:
    """Data Access Object for predictions table."""
    
    @staticmethod
    def create_prediction(report_id, disease_id, prediction_result, confidence_score, 
                         method='DSA', dsa_result_id=None, ml_result_id=None):
        """Create a prediction record."""
        query = """
            INSERT INTO predictions (report_id, disease_id, prediction_result, confidence_score, 
                                   method, dsa_result_id, ml_result_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            prediction_id = DatabaseConnection.execute_query(
                query,
                (report_id, disease_id, prediction_result, confidence_score, 
                 method, dsa_result_id, ml_result_id),
                fetch=False
            )
            return prediction_id
        except Error as e:
            print(f"Error creating prediction: {e}")
            return None
    
    @staticmethod
    def get_predictions_by_report(report_id):
        """Get all predictions for a report."""
        query = """
            SELECT p.*, dm.disease_name
            FROM predictions p
            JOIN disease_models dm ON p.disease_id = dm.id
            WHERE p.report_id = %s
            ORDER BY p.confidence_score DESC
        """
        return DatabaseConnection.execute_query(query, (report_id,))
    
    @staticmethod
    def get_predictions_by_patient(patient_id):
        """Get all predictions for a patient."""
        query = """
            SELECT p.*, dm.disease_name, pr.created_at as report_date
            FROM predictions p
            JOIN disease_models dm ON p.disease_id = dm.id
            JOIN patient_reports pr ON p.report_id = pr.id
            WHERE pr.patient_id = %s
            ORDER BY pr.created_at DESC, p.confidence_score DESC
        """
        return DatabaseConnection.execute_query(query, (patient_id,))


class LoginHistoryDAO:
    """Data Access Object for login_history table."""
    
    @staticmethod
    def create_login_record(user_id, ip_address, user_agent, success=True):
        """Create a login history record."""
        query = """
            INSERT INTO login_history (user_id, ip_address, user_agent, success)
            VALUES (%s, %s, %s, %s)
        """
        try:
            record_id = DatabaseConnection.execute_query(
                query,
                (user_id, ip_address, user_agent, success),
                fetch=False
            )
            return record_id
        except Error as e:
            print(f"Error creating login record: {e}")
            return None
    
    @staticmethod
    def get_user_login_history(user_id, limit=10):
        """Get login history for a user."""
        query = """
            SELECT * FROM login_history
            WHERE user_id = %s
            ORDER BY login_time DESC
            LIMIT %s
        """
        return DatabaseConnection.execute_query(query, (user_id, limit))

