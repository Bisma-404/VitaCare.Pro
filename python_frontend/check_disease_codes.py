from database.db_connection import DatabaseConnection

with DatabaseConnection.get_connection() as conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, disease_name, disease_code FROM disease_models')
    diseases = cursor.fetchall()
    print('Disease models:')
    for d in diseases:
        print(f'  {d["id"]}: {d["disease_name"]} -> {d["disease_code"]}')
    cursor.close()