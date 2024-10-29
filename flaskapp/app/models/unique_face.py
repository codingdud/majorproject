from app.database import db
import numpy as np

class UniqueFace(db.Model):
    __tablename__ = 'unique_faces'

    uid = db.Column(db.Integer, primary_key=True)
    features = db.Column(db.LargeBinary)  # Binary data for face features
    image_paths = db.Column(db.ARRAY(db.Text))  # Array of image paths
    pid = db.Column(db.Integer, db.ForeignKey('projects.pid'), nullable=True)  # Foreign key to Projects table
    label = db.Column(db.String(100), default="name")  # Label for the unique face

    def __repr__(self):
        return f'<UniqueFace {self.uid}>'

    @classmethod
    def insert_unique_face(cls, created_face_features, pid=None, tolerance=0.53):
        for face_feature in created_face_features:
            features = face_feature.features  # Get the features from the created face feature
            features_array = np.frombuffer(features, dtype=np.float64)

            # Check for matches in the UniqueFace table
            query = cls.query
            if pid is not None:
                query = query.filter_by(pid=pid)
            
            is_matched = False  # Flag to check if a match was found
            for unique_face in query.all():
                db_features = np.frombuffer(unique_face.features, dtype=np.float64)
                distance = np.linalg.norm(features_array - db_features)

                if distance < tolerance:
                    # If a match is found, update the image paths
                    existing_paths = unique_face.image_paths  # Get the existing image paths

                    # Ensure image_paths is a list if it's not already
                    if isinstance(existing_paths, list):
                        existing_paths.append(face_feature.image_paths)  # Append new image path
                    else:
                        existing_paths = [existing_paths, face_feature.image_paths]  # Create list if necessary
                    
                    unique_face.image_paths = existing_paths  # Update the unique_face with the new list
                    is_matched = True
                    continue  # Continue to the next face feature

            if not is_matched:
                # If no match was found, create a new UniqueFace entry
                new_unique_face = cls(
                    features=features,
                    image_paths=[face_feature.image_paths],  # Store as a list
                    pid=pid
                )
                db.session.add(new_unique_face)

        # Commit the changes to the database
        db.session.commit()

    @classmethod
    def get_faces_by_pid(cls, pid):
        """Retrieve all unique faces for a given PID."""
        return cls.query.filter_by(pid=pid).all()
        
    @classmethod
    def update_unique_face(cls, uid, updated_data):
        """Update an existing unique face."""
        unique_face = cls.query.get(uid)
        if unique_face:
            for key, value in updated_data.items():
                setattr(unique_face, key, value)  # Set the new value for each field
            db.session.commit()
            return unique_face
        return None  # Return None if not found

    @classmethod
    def delete_unique_face(cls, uid):
        """Delete a unique face."""
        unique_face = cls.query.get(uid)
        if unique_face:
            db.session.delete(unique_face)
            db.session.commit()
            return True  # Return True if deleted successfully
        return False  # Return False if not found