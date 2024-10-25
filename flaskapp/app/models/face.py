from app.database import db
import numpy as np
from sqlalchemy.dialects.postgresql import ARRAY

class Face(db.Model):
    __tablename__ = 'faces'
    
    id = db.Column(db.Integer, primary_key=True)
    features = db.Column(ARRAY(db.Float))  # Store face features as array
    image_paths = db.Column(db.Text)  # Store comma-separated image paths
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Face {self.id}>'
    
    @staticmethod
    def find_matches(features, tolerance=0.53):
        """Find matching faces in database"""
        matches = []
        for face in Face.query.all():
            distance = np.linalg.norm(np.array(features) - np.array(face.features))
            if distance < tolerance:
                matches.extend(face.image_paths.split(','))
        return list(set(matches))
