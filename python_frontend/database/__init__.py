"""
Database package for hospital management system.
"""

from .db_connection import DatabaseConnection, init_db
__all__ = ['DatabaseConnection', 'init_db']

