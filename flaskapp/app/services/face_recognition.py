import cv2
import dlib
import numpy as np
import os
from flask import current_app

class FaceRecognitionService:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(current_app.config['DLIB_SHAPE_PREDICTOR'])
        self.face_rec_model = dlib.face_recognition_model_v1(current_app.config['DLIB_FACE_RECOGNITION'])

    def get_face_features(self, image, face_rect):
        """Extract facial features from a face rectangle."""
        shape = self.predictor(image, face_rect)
        face_descriptor = self.face_rec_model.compute_face_descriptor(image, shape)
        return np.array(face_descriptor)

    def process_image(self, image_path):
        """Process input image to extract facial features."""
        image = cv2.imread(image_path)
        if image is None:
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        if len(faces) == 0:
            return None

        # Return features for the first detected face
        return self.get_face_features(image, faces[0])

    def process_image2(self, file):
        """
        Process an image file to extract facial features.
        """
        # Reset the file pointer to the beginning
        file.seek(0)
        # Read the file directly into a NumPy array
        file_data = np.frombuffer(file.read(), np.uint8)
        # Decode the image from memory
        image = cv2.imdecode(file_data, cv2.IMREAD_COLOR)
        
        if image is None:
            return None

        # Convert to grayscale if needed
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        if len(faces) == 0:
            return None

        # Return features for the first detected face
        return self.get_face_features(image, faces[0])
