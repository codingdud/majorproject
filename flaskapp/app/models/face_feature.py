from app.database import db
from datetime import datetime
import numpy as np

class FaceFeature(db.Model):
    __tablename__ = 'face_features'

    id = db.Column(db.Integer, primary_key=True)
    features = db.Column(db.LargeBinary)
    asset_id = db.Column(db.String, nullable=False)  # New field for Cloudinary asset ID
    url = db.Column(db.String, nullable=False)       # New field for Cloudinary URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pid = db.Column(db.Integer, db.ForeignKey('projects.pid'), nullable=True)

    def __repr__(self):
        return f'<FaceFeature {self.id}>'

    @staticmethod
    def find_matches(features, pid=None, tolerance=0.53):
        matches = []
        features_array = np.frombuffer(features, dtype=np.float64)

        # Filter FaceFeature records by pid if provided
        query = FaceFeature.query
        if pid is not None:
            query = query.filter_by(pid=pid)
        
        for face in query.all():
            db_features = np.frombuffer(face.features, dtype=np.float64)
            distance = np.linalg.norm(features_array - db_features)
            if distance < tolerance:
                matches.append(face)  # Use URL instead of image paths

        return list(set(matches))

    # Create a new face feature
    @staticmethod
    def create_face_feature(features, asset_id, url, pid):
        new_face_feature = FaceFeature(features=features, asset_id=asset_id, url=url, pid=pid)
        db.session.add(new_face_feature)
        db.session.commit()
        return new_face_feature

    # Get all face features
    @staticmethod
    def get_all_face_features():
        return FaceFeature.query.all()

    # Get a face feature by ID
    @staticmethod
    def get_face_feature_by_id(face_feature_id):
        return FaceFeature.query.get(face_feature_id)

    # Update a face feature
    @staticmethod
    def update_face_feature(face_feature_id, features=None, asset_id=None, url=None):
        face_feature = FaceFeature.query.get(face_feature_id)
        if face_feature:
            if features is not None:
                face_feature.features = features
            if asset_id is not None:
                face_feature.asset_id = asset_id
            if url is not None:
                face_feature.url = url
            db.session.commit()
            return face_feature
        return None

    # Delete a face feature
    @staticmethod
    def delete_face_feature(id):
        face_feature = FaceFeature.query.get(id)
        if face_feature:
            db.session.delete(face_feature)
            db.session.commit()
            return True
        return False

    # Get face features by project ID
    @staticmethod
    def get_face_features_by_pid(pid):
        return FaceFeature.query.filter_by(pid=pid).all()
