from app.database import db
import numpy as np

class UniqueFace(db.Model):
    __tablename__ = 'unique_faces'

    uid = db.Column(db.Integer, primary_key=True)
    features = db.Column(db.LargeBinary)  # Binary data for face features
    asset_ids = db.Column(db.ARRAY(db.String))  # Array of Cloudinary asset IDs
    urls = db.Column(db.ARRAY(db.String))       # Array of Cloudinary URLs
    pid = db.Column(db.Integer, db.ForeignKey('projects.pid'), nullable=True)  # Foreign key to Projects table
    label = db.Column(db.String(100), default="name")  # Label for the unique face

    def __repr__(self):
        return f'<UniqueFace {self.uid}>'

    @classmethod
    def insert_unique_face(cls, created_face_features, pid=None, tolerance=0.53):
        try:
            # Check for matches in the UniqueFace table
            query = cls.query
            if pid is not None:
                query = query.filter_by(pid=pid)
            array = query.all()

            for face_feature in created_face_features:
                features = face_feature.features
                features_array = np.frombuffer(features, dtype=np.float64)

                is_matched = False
                for unique_face in array:
                    db_features = np.frombuffer(unique_face.features, dtype=np.float64)
                    distance = np.linalg.norm(features_array - db_features)

                    if distance < tolerance:
                        try:
                            # Create new lists from existing data
                            existing_asset_ids = list(unique_face.asset_ids) if unique_face.asset_ids else []
                            existing_urls = list(unique_face.urls) if unique_face.urls else []

                            # Append new values if they don't already exist
                            if face_feature.asset_id not in existing_asset_ids:
                                existing_asset_ids.append(face_feature.asset_id)
                            if face_feature.url not in existing_urls:
                                existing_urls.append(face_feature.url)

                            # Update the attributes
                            unique_face.asset_ids = existing_asset_ids
                            unique_face.urls = existing_urls

                            # Explicitly mark as modified
                            db.session.merge(unique_face)
                            
                            # Flush to ensure changes are tracked
                            db.session.flush()
                            
                            is_matched = True
                            print(f"Updated face {unique_face.uid} with new assets: {existing_asset_ids}")
                            break  # Exit the loop once we find a match
                            
                        except Exception as e:
                            print(f"Error updating existing face: {e}")
                            raise

                if not is_matched:
                    try:
                        # If no match was found, create a new UniqueFace entry
                        new_unique_face = cls(
                            features=features,
                            asset_ids=[face_feature.asset_id],
                            urls=[face_feature.url],
                            pid=pid
                        )
                        # Add the new face to our working array
                        array.append(new_unique_face)
                        db.session.add(new_unique_face)
                        db.session.flush()
                        print(f"Added new unique face with asset: {face_feature.id}")
                        
                    except Exception as e:
                        print(f"Error creating new face: {e}")
                        raise

            # Commit all changes to the database
            try:
                db.session.commit()
                print("All changes committed successfully")
                return True
                
            except Exception as e:
                print(f"Failed to commit changes: {e}")
                db.session.rollback()
                raise

        except Exception as e:
            print(f"An error occurred during face insertion: {e}")
            db.session.rollback()
            return False


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
