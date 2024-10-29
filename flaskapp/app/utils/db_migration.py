import sqlite3
import psycopg2
import numpy as np
import os
from app.database import db
from app.models.face import Face
from app.models.migration_status import MigrationStatus

class DBMigrationUtil:
    MIGRATION_NAME = 'sqlite_to_postgres_faces'

    def __init__(self, postgres_conn_details, sqlite_path='facial_features.db'):
        self.postgres_conn_details = postgres_conn_details
        self.sqlite_path = sqlite_path

    def should_migrate(self):
        try:
            if MigrationStatus.is_migrated(self.MIGRATION_NAME):
                print("Migration was already completed.")
                return False

            if not os.path.exists(self.sqlite_path):
                print("SQLite database not found.")
                return False

            count = Face.query.count()
            if count > 0:
                print("PostgreSQL database already contains data.")
                return False

            return True

        except Exception as e:
            print(f"Error checking migration status: {str(e)}")
            return False

    def migrate(self):
        """Migrate data from SQLite to PostgreSQL"""
        if not self.should_migrate():
            return False

        sqlite_conn = None
        postgres_conn = None
        try:
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_cursor = sqlite_conn.cursor()

            # Connect to PostgreSQL
            postgres_conn = psycopg2.connect(**self.postgres_conn_details)
            postgres_cursor = postgres_conn.cursor()

            # Start transaction
            postgres_conn.autocommit = False

            # Get data from SQLite
            sqlite_cursor.execute('SELECT id, features, image_paths FROM Faces')
            rows = sqlite_cursor.fetchall()

            # Migrate data
            for row in rows:
                sqlite_id, sqlite_features, sqlite_image_paths = row
                
                # Ensure features is not None before processing
                if sqlite_features is not None:
                    # Convert SQLite binary data to PostgreSQL binary format directly
                    postgres_features = psycopg2.Binary(sqlite_features)
                else:
                    postgres_features = None  # Handle None features if necessary
                
                # Insert into PostgreSQL
                insert_query = '''
                INSERT INTO faces (features, image_paths)
                VALUES (%s, %s)
                '''
                postgres_cursor.execute(insert_query, (sqlite_features, sqlite_image_paths))

            # Mark migration as completed
            MigrationStatus.mark_as_migrated(self.MIGRATION_NAME)
            
            # Commit transaction
            postgres_conn.commit()
            print("Data migration completed successfully!")
            return True

        except Exception as e:
            # Rollback in case of error
            if postgres_conn:
                postgres_conn.rollback()
            print(f"Error during data migration: {str(e)}")
            return False

        finally:
            # Close connections
            if sqlite_cursor:
                sqlite_cursor.close()
            if sqlite_conn:
                sqlite_conn.close()
            if postgres_cursor:
                postgres_cursor.close()
            if postgres_conn:
                postgres_conn.close()
