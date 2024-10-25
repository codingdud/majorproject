from flask import Blueprint, request, jsonify, current_app
from app.services.face_recognition import FaceRecognitionService
from app.models.face import Face
from werkzeug.utils import secure_filename
import os

face_bp = Blueprint('face', __name__)

@face_bp.route('/ok', methods=['GET'])
def index():
    return {"message": "I am ok!"}

@face_bp.route("/user/<id>", methods=['GET', 'POST'])
def api(id):
    if request.method == 'GET':
        return {'id': id}
    return jsonify({'error': 'Method not allowed'}), 405

@face_bp.route("/facefinder", methods=['POST'])
def facefinder():
    if 'image' not in request.files and 'path' not in request.form:
        return jsonify({'error': 'No image file or path provided'}), 400

    face_service = FaceRecognitionService()
    
    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
    else:
        filepath = request.form['path']

    # Process image and extract features
    features = face_service.process_image(filepath)
    
    if features is None:
        return jsonify({'message': 'No faces found in image'}), 404

    # Find matching images
    matching_images = Face.find_matches(features)
    
    if matching_images:
        return jsonify({'matching_images': matching_images}), 200
    else:
        return jsonify({'message': 'No matching images found'}), 404