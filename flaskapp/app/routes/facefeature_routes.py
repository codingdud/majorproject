from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
import numpy as np
from app.services.face_recognition import FaceRecognitionService
from app.models.face_feature import FaceFeature
from app.models.unique_face import UniqueFace
from app.database import db
import asyncio


facefeature_bp = Blueprint('facefeature', __name__)

@facefeature_bp.route("/imagesupload/<int:pid>", methods=['POST'])
async def create_face_feature(pid):
    if 'images' not in request.files:
        return jsonify({'error': 'Missing image'}), 400

    face_service = FaceRecognitionService()
    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400
    if not pid:
        return jsonify({'error': 'pid missing'}), 400    

    saved_file_paths = []
    
    for file in files:
        filename = secure_filename(file.filename)
        if filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the folder exists
        file.save(filepath)
        saved_file_paths.append(filepath)

    # Create FaceFeature entries for each uploaded image
    created_face_features = []
    for path in saved_file_paths:
        features = face_service.process_image(path)
        if features is not None:
            face_feature = FaceFeature.create_face_feature(features=features, image_paths=path, pid=pid)
            created_face_features.append(face_feature)
            
    # Call the insert_unique_face function asynchronously
    await asyncio.to_thread(UniqueFace.insert_unique_face, created_face_features, pid)
    response_data = []

    for face_feature in created_face_features:
        # Convert binary features to numpy array
        features_array = np.frombuffer(face_feature.features, dtype=np.float64)
        
        # Prepare response data for each feature, extracting the first element from features_array
        response_data.append({
            'id': face_feature.id,
            'features': features_array.tolist()[0],  # Extracting the first element
            'image_paths': face_feature.image_paths,
            'created_at': face_feature.created_at.isoformat(),
            'pid': face_feature.pid
        })

    return jsonify({'message': 'Face features created', 'files': response_data}), 201

@facefeature_bp.route("/<int:id>", methods=['GET'])
def get_face_feature(id):
    face_feature = FaceFeature.get_face_feature_by_id(id)
    if not face_feature:
        return jsonify({'error': 'Face feature not found'}), 404

    features_array = np.frombuffer(face_feature.features, dtype=np.float64)
    return jsonify({
        'id': face_feature.id,
        'features': features_array.tolist()[0],
        'image_paths': face_feature.image_paths,
        'created_at': face_feature.created_at.isoformat(),
        'pid': face_feature.pid
    }), 200

@facefeature_bp.route("/pid/<int:pid>", methods=['GET'])
def get_face_features_by_pid(pid):
    face_features = FaceFeature.get_face_features_by_pid(pid)
    if not face_features:
        return jsonify({'error': 'No face features found for this PID'}), 404

    # Prepare the response data
    response_data = []
    for face_feature in face_features:
        features_array = np.frombuffer(face_feature.features, dtype=np.float64)
        response_data.append({
            'id': face_feature.id,
            'features': features_array.tolist()[0],
            'image_paths': face_feature.image_paths,
            'created_at': face_feature.created_at.isoformat(),
            'pid': face_feature.pid
        })

    return jsonify(response_data), 200

@facefeature_bp.route("/<int:id>", methods=['PUT'])
def update_face_feature(id):
    face_feature = FaceFeature.get_face_feature_by_id(id)
    if not face_feature:
        return jsonify({'error': 'Face feature not found'}), 404

    data = request.json
    if 'pid' in data:
        face_feature.pid = data['pid']

    db.session.commit()

    return jsonify({'message': 'Face feature updated'}), 200

@facefeature_bp.route("/<int:id>", methods=['DELETE'])
def delete_face_feature(id):
    if not FaceFeature.delete_face_feature(id):
        return jsonify({'error': 'Face feature not found'}), 404

    return jsonify({'message': 'Face feature deleted'}), 200

@facefeature_bp.route("/facefinder/<int:pid>", methods=['POST'])
def facefinder(pid):
    if 'image' not in request.files and 'path' not in request.form:
        return jsonify({'error': 'No image file or path provided'}), 400

    face_service = FaceRecognitionService()
    
    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the folder exists
        file.save(filepath)
    else:
        filepath = request.form['path']

    features = face_service.process_image(filepath)
    
    if features is None:
        return jsonify({'message': 'No faces found in image'}), 404

    matching_images = FaceFeature.find_matches(features,pid)

    if matching_images:
        return jsonify({'matching_images': matching_images}), 200
    else:
        return jsonify({'message': 'No matching images found'}), 404

@facefeature_bp.route('/images/<path:filename>', methods=['GET'])
def get_uploaded_file(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    print(f"Serving file from: {upload_folder}/{filename}")
    try:
        return send_from_directory(os.getcwd(), filename)
    except FileNotFoundError:
        abort(404)
