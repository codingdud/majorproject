import sqlite3
import psycopg2
import numpy as np

# SQLite and PostgreSQL connection details
# PostgreSQL connection details with SSL


# Step 1: Connect to SQLite
sqlite_conn = sqlite3.connect('facial_features.db')
sqlite_cursor = sqlite_conn.cursor()

# Step 2: Connect to PostgreSQL
postgres_conn = psycopg2.connect(**postgres_conn_details)
postgres_cursor = postgres_conn.cursor()

# Step 3: Create PostgreSQL Table (if it doesn't exist)
create_table_query = '''
CREATE TABLE IF NOT EXISTS Faces (
    id SERIAL PRIMARY KEY,
    features BYTEA,  -- Storing facial encodings as binary
    image_paths TEXT  -- Storing image file paths
);
'''
postgres_cursor.execute(create_table_query)
postgres_conn.commit()

# Step 4: Fetch data from SQLite
sqlite_cursor.execute('SELECT id, features, image_paths FROM Faces')
rows = sqlite_cursor.fetchall()

# Step 5: Insert data into PostgreSQL
for row in rows:
    sqlite_id, sqlite_features, sqlite_image_paths = row
    
    # Convert SQLite binary data to numpy array
    np_features = np.frombuffer(sqlite_features, dtype=np.float64)
    
    # Prepare the PostgreSQL binary data
    postgres_features = psycopg2.Binary(np_features.tobytes())
    
    # Insert into PostgreSQL
    insert_query = '''
    INSERT INTO Faces (features, image_paths)
    VALUES (%s, %s)
    '''
    postgres_cursor.execute(insert_query, (postgres_features, sqlite_image_paths))
    postgres_conn.commit()

# Step 6: Close connections
sqlite_conn.close()
postgres_conn.close()

print("Data migration from SQLite to PostgreSQL is complete!")
