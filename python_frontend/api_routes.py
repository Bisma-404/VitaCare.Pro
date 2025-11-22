"""
API stub: original JSON API was removed to simplify the project.
This module leaves a minimal `api_bp` Blueprint so the app can import safely.
If you want the API restored later, revert this file from git history.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Intentionally empty: API endpoints were removed per cleanup request.
