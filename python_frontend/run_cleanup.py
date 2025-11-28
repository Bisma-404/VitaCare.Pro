from database.db_connection import DatabaseConnection

def run_sql_file(filename):
    """Execute SQL commands from a file."""
    try:
        with open(filename, 'r') as file:
            sql_content = file.read()

        # Split the SQL content into individual statements
        statements = []
        current_statement = ""
        in_multiline_comment = False

        for line in sql_content.split('\n'):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue

            # Handle multiline comments
            if '/*' in line:
                in_multiline_comment = True
            if '*/' in line:
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue

            # Build current statement
            current_statement += line + " "

            # Check if statement is complete (ends with semicolon)
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""

        # Execute each statement
        for statement in statements:
            if statement.strip():
                print(f"Executing: {statement[:50]}...")
                if statement.strip().upper().startswith('SELECT'):
                    result = DatabaseConnection.execute_query(statement)
                    if result:
                        print(f"Result: {result}")
                else:
                    DatabaseConnection.execute_query(statement, fetch=False)
                print("✓ Executed successfully")

        print("\n🎉 Database cleanup completed successfully!")

    except Exception as e:
        print(f"❌ Error executing SQL file: {e}")

if __name__ == "__main__":
    run_sql_file("cleanup_database.sql")