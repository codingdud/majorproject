import sqlite3
import psycopg2
import numpy as np
import os
from flask import current_app
from app.database import db
from app.models.face import Face
from app.models.migration_status import MigrationStatus

class DBMigrationUtil:
    MIGRATION_NAME = 'sqlite_to_postgres_faces'

    def __init__(self, postgres_conn_details, sqlite_path='facial_features.db'):
        self.postgres_conn_details = postgres_conn_details
        self.sqlite_path = sqlite_path

    def should_migrate(self):
        """
        Check if migration is needed by verifying:
        1. Migration hasn't been completed before
        2. SQLite database exists
        3. PostgreSQL faces table is empty
        """
        try:
            # Check if migration was already completed
            if MigrationStatus.is_migrated(self.MIGRATION_NAME):
                print("Migration was already completed.")
                return False

            # Check if SQLite database exists
            if not os.path.exists(self.sqlite_path):
                print("SQLite database not found.")
                return False

            # Check if PostgreSQL faces table is empty
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

        try:
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_cursor = sqlite_conn.cursor()

            # Connect to PostgreSQL
            postgres_conn = psycopg2.connect(**self.postgres_conn_details)
            postgres_cursor = postgres_conn.cursor()

            # Start transaction
            postgres_conn.autocommit = False

            try:
                # Get data from SQLite
                sqlite_cursor.execute('SELECT id, features, image_paths FROM Faces')
                rows = sqlite_cursor.fetchall()

                # Migrate data
                for row in rows:
                    sqlite_id, sqlite_features, sqlite_image_paths = row
                    
                    # Convert SQLite binary data to numpy array
                    np_features = np.frombuffer(sqlite_features, dtype=np.float64)
                    
                    # Convert to PostgreSQL binary format
                    postgres_features = psycopg2.Binary(np_features.tobytes())
                    
                    # Insert into PostgreSQL
                    insert_query = '''
                    INSERT INTO faces (features, image_paths)
                    VALUES (%s, %s)
                    '''
                    postgres_cursor.execute(insert_query, (postgres_features, sqlite_image_paths))

                # Mark migration as completed
                MigrationStatus.mark_as_migrated(self.MIGRATION_NAME)
                
                # Commit transaction
                postgres_conn.commit()
                print("Data migration completed successfully!")
                return True

            except Exception as e:
                # Rollback in case of error
                postgres_conn.rollback()
                raise e

        except Exception as e:
            print(f"Migration failed: {str(e)}")
            return False

        finally:
            # Close connections
            try:
                sqlite_cursor.close()
                sqlite_conn.close()
                postgres_cursor.close()
                postgres_conn.close()
            except:
                pass