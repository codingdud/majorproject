from flask import Flask
from app.config import Config
from app.database import db
from app.routes.face_routes import face_bp
from app.routes.auth_routes import user_bp
from app.routes.project_routes import project_bp
from app.routes.facefeature_routes import facefeature_bp


from app.utils.db_migration import DBMigrationUtil
from flask_migrate import Migrate
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(face_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/auth')
    app.register_blueprint(project_bp, url_prefix='/project')
    app.register_blueprint(facefeature_bp, url_prefix='/facefeature')

    
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Initialize migration utility
        migration_util = DBMigrationUtil(
            postgres_conn_details=app.config['POSTGRES_CONN_DETAILS'],
            sqlite_path=app.config['SQLITE_DB_PATH']
        )
        
        # Attempt migration if needed
        migration_util.migrate()
    
    return app