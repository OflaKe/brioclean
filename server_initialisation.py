import sqlite3

def save_measurements(data):
    # Step 1: Establish connection
    conn = sqlite3.connect('data.db')

    # Step 2: Create cursor
    cursor = conn.cursor()

    # Step 3: Define the table name and measurement names
    table_name = 'measurements'
    measurement_names = ['measurement1', 'measurement2']

    # Step 4: Generate the CREATE TABLE statement dynamically
    columns = ', '.join([f"{name} REAL" for name in measurement_names])
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})"

    # Step 5: Execute the CREATE TABLE statement
    cursor.execute(create_table_query)

    # Step 6: Read data from the data list
    data = data[-2:]  # Example: Get the last two data points

    # Step 7: Generate the INSERT INTO statement dynamically
    values = ', '.join(['?' for _ in measurement_names])
    insert_query = f"INSERT INTO {table_name} ({', '.join(measurement_names)}) VALUES ({values})"

    # Step 8: Execute the INSERT INTO statement for each data point
    for item in data:
        cursor.execute(insert_query, (item,))

    # Step 9: Commit the changes
    conn.commit()

    # Step 10: Close cursor and connection
    cursor.close()
    conn.close()
