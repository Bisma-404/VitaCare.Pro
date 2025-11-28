from database.db_connection import DatabaseConnection

with DatabaseConnection.get_connection() as conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT dt.*, dm.disease_name FROM disease_thresholds dt JOIN disease_models dm ON dt.disease_id = dm.id ORDER BY dm.disease_name, dt.parameter_name')
    thresholds = cursor.fetchall()
    print(f'Total thresholds in database: {len(thresholds)}')
    print()
    for t in thresholds:
        print(f'{t["disease_name"]} - {t["parameter_name"]}: {t["min_value"]} - {t["max_value"]} {t["unit"]}')
    cursor.close()