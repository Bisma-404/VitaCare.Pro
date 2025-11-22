"""
Database connection utility using mysql-connector-python.
Provides centralized database connection management.
"""

import mysql.connector
from mysql.connector import Error, pooling
import os
from contextlib import contextmanager


class DatabaseConnection:
    """Manages MySQL database connections using connection pooling."""
    
    _connection_pool = None
    _config = None
    
    @classmethod
    def initialize(cls, config=None):
        """Initialize database connection pool."""
        if config is None:
            config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'hospital_management_db'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', 'abcd1234'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'pool_name': 'hospital_pool',
                'pool_size': 10,
                'pool_reset_session': True,
                'autocommit': False, 'auth_plugin': 'mysql_native_password'
            }
        
        cls._config = config
        
        try:
            cls._connection_pool = pooling.MySQLConnectionPool(
                **config
            )
            print(f"✅ Database connection pool created: {config['database']}")
        except Error as e:
            print(f"❌ Error creating connection pool: {e}")
            raise
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """Get a database connection from the pool (context manager)."""
        if cls._connection_pool is None:
            cls.initialize()
        
        connection = None
        try:
            connection = cls._connection_pool.get_connection()
            yield connection
            connection.commit()
        except Error as e:
            if connection:
                connection.rollback()
            print(f"❌ Database error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @classmethod
    def get_connection_manual(cls):
        """Get a database connection manually (non-context manager)."""
        if cls._connection_pool is None:
            cls.initialize()
        
        try:
            connection = cls._connection_pool.get_connection()
            return connection
        except Error as e:
            print(f"❌ Error getting connection: {e}")
            raise
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """Execute a query and return results."""
        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                if fetch:
                    if query.strip().upper().startswith('SELECT'):
                        return cursor.fetchall()
                    return cursor.rowcount
                else:
                    # For INSERT/UPDATE/DELETE, return lastrowid if available
                    connection.commit()
                    if query.strip().upper().startswith('INSERT'):
                        return cursor.lastrowid
                    return cursor.rowcount
            finally:
                cursor.close()
    
    @classmethod
    def execute_many(cls, query, params_list):
        """Execute a query multiple times with different parameters."""
        with cls.get_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.executemany(query, params_list)
                return cursor.rowcount
            finally:
                cursor.close()
    
    @classmethod
    def test_connection(cls):
        """Test database connection."""
        try:
            with cls.get_connection() as connection:
                # Use buffered cursor to ensure any results are consumed, preventing
                # "Unread result found" errors when executing simple test queries.
                cursor = connection.cursor(buffered=True)
                cursor.execute("SELECT 1")
                # Fetch any results to clear the result set before closing cursor.
                try:
                    cursor.fetchall()
                except Exception:
                    # If fetch fails for some reason, ignore — we only need to clear results.
                    pass
                cursor.close()
                return True
        except Error as e:
            print(f"❌ Connection test failed: {e}")
            return False


def init_db(config=None):
    """Initialize database connection."""
    DatabaseConnection.initialize(config)


def get_db_connection():
    """Get a raw database connection (for backward compatibility)."""
    if DatabaseConnection._connection_pool is None:
        DatabaseConnection.initialize()
    return DatabaseConnection._connection_pool.get_connection()
