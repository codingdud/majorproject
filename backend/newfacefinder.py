import cv2
import dlib
import numpy as np
import sqlite3

# Global definitions for dlib face detector and models
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_rec_model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')

def get_face_features(image, face_rect):
    """Extract the 128D facial features from a face rectangle."""
    shape = predictor(image, face_rect)
    face_descriptor = face_rec_model.compute_face_descriptor(image, shape)
    return np.array(face_descriptor)

def find_matching_images(features, tolerance=0.53):
    """Find all images in the database that match the given facial features."""
    conn = sqlite3.connect('facial_features.db')  # Create a new connection
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, features, image_paths FROM Faces')
    matching_images = []
    
    for row in cursor.fetchall():
        db_id, db_features, image_paths = row
        db_features = np.frombuffer(db_features, dtype=np.float64)
        distance = np.linalg.norm(features - db_features)
        if distance < tolerance:
            matching_images.extend(image_paths.split(','))
    
    conn.close()  # Close the connection after use
    return matching_images

def process_input_image(image_path):
    """Process the input image to find all matching images in the database."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)  # Now `detector` is properly initialized

    if len(faces) == 0:
        print(f"No faces found in {image_path}")
        return []

    all_matching_images = set()
    for face in faces:
        features = get_face_features(image, face)
        matching_images = find_matching_images(features)
        all_matching_images.update(matching_images)
    
    return list(all_matching_images)

def list_of_match_images(input_image_path):
    """Interface to process an image and return matching images."""
    matching_images = process_input_image(input_image_path)
    return matching_images
