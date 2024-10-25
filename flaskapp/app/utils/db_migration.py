import sqlite3
import psycopg2
import numpy as np
import os
from flask import current_app
from app.database import db
from app.models.face import Face

class DBMigrationUtil:
    def __init__(self, postgres_conn_details, sqlite_path='facial_features.db'):
        self.postgres_conn_details = postgres_conn_details
        self.sqlite_path = sqlite_path

    def should_migrate(self):
        """Check if migration is needed by verifying if Faces table is empty"""
        try:
            count = Face.query.count()
            return count == 0 and os.path.exists(self.sqlite_path)
        except:
            return False

    def migrate(self):
        """Migrate data from SQLite to PostgreSQL"""
        if not self.should_migrate():
            print("Migration not needed or SQLite database not found.")
            return False

        try:
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_cursor = sqlite_conn.cursor()

            # Connect to PostgreSQL
            postgres_conn = psycopg2.connect(**self.postgres_conn_details)
            postgres_cursor = postgres_conn.cursor()

            # Get data from SQLite
            sqlite_cursor.execute('SELECT id, features, image_paths FROM Faces')
            rows = sqlite_cursor.fetchall()

            # Migrate data
            for row in rows:
                sqlite_id, sqlite_features, sqlite_image_paths = row
                
                # Convert SQLite binary data to numpy array
                np_features = np.frombuffer(sqlite_features, dtype=np.float64)
    
                # Prepare the PostgreSQL binary data
                postgres_features = psycopg2.Binary(np_features.tobytes())
                
                # Insert into PostgreSQL
                insert_query = '''
                INSERT INTO faces (features, image_paths)
                VALUES (%s, %s)
                '''
                postgres_cursor.execute(insert_query, (sqlite_features, sqlite_image_paths))
                postgres_conn.commit()

            # Close connections
            sqlite_cursor.close()
            sqlite_conn.close()
            postgres_cursor.close()
            postgres_conn.close()

            print("Data migration from SQLite to PostgreSQL completed successfully!")
            return True

        except Exception as e:
            print(f"Migration failed: {str(e)}")
            return False
