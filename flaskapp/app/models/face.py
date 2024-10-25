from app.database import db
import numpy as np

class Face(db.Model):
    __tablename__ = 'faces'  # Specify the name of the table

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    features = db.Column(db.LargeBinary)  # Use LargeBinary for binary data storage
    image_paths = db.Column(db.Text)  # Store image paths as a comma-separated string
    created_at = db.Column(db.DateTime, server_default=db.func.now())  # Auto-generated timestamp

    def __repr__(self):
        return f'<Face {self.id}>'

    @staticmethod
    def find_matches(features, tolerance=0.53):
        """Find matching faces in the database based on features and a given tolerance."""
        matches = []

        # Convert input features to a numpy array
        features_array = np.frombuffer(features, dtype=np.float64)

        for face in Face.query.all():
            db_features = np.frombuffer(face.features, dtype=np.float64)
            distance = np.linalg.norm(features_array - db_features)
            if distance < tolerance:
                # If a match is found, add the image paths to the list
                matches.extend(face.image_paths.split(','))

        # Return unique matches
        return list(set(matches))
