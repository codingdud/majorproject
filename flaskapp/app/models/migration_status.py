# app/models/migration_status.py
from app.database import db
from datetime import datetime

class MigrationStatus(db.Model):
    __tablename__ = 'migration_status'
    
    id = db.Column(db.Integer, primary_key=True)
    migration_name = db.Column(db.String(255), unique=True)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    @staticmethod
    def is_migrated(migration_name):
        status = MigrationStatus.query.filter_by(migration_name=migration_name).first()
        return status is not None and status.completed

    @staticmethod
    def mark_as_migrated(migration_name):
        status = MigrationStatus.query.filter_by(migration_name=migration_name).first()
        if not status:
            status = MigrationStatus(migration_name=migration_name)
        
        status.completed = True
        status.completed_at = datetime.utcnow()
        db.session.add(status)
        db.session.commit()