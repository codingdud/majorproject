from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
import numpy as np
from app.services.face_recognition import FaceRecognitionService
from app.models.face_feature import FaceFeature
from app.models.unique_face import UniqueFace
from app.database import db
from app.utils.cloudinary import CloudinaryUtil
from cloudinary import  exceptions

import asyncio

# Define the blueprint for face feature routes
facefeature_bp = Blueprint('facefeature', __name__)

# Route to upload multiple face images, extract features, and save them
@facefeature_bp.route("/imagesupload/<int:pid>", methods=['POST'])
async def create_face_feature(pid):
    # Check for 'images' in request files
    if 'images' not in request.files:
        return jsonify({'error': 'Missing image'}), 400
    cloud = CloudinaryUtil()
    face_service = FaceRecognitionService()
    files = request.files.getlist('images')  # Retrieve all uploaded files
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400
    if not pid:
        return jsonify({'error': 'pid missing'}), 400    

    saved_file_paths = []
    created_face_features=[]
    # Save each uploaded file
    for file in files:
        filename = secure_filename(file.filename)
        if filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        if cloud:
            result=cloud.upload_image(file)
            #print(result)
            features = face_service.process_image2(file)
            if features is not None:
                face_feature=FaceFeature.create_face_feature(features, result["asset_id"], result["url"], pid)
                created_face_features.append(face_feature)
        else:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure folder exists
            file.save(filepath)
            features = face_service.process_image(path)
            if features is not None:
                face_feature = FaceFeature.create_face_feature(features=features, asset_id=0, url=filepath, pid=pid)
                created_face_features.append(face_feature)
            

    # Prepare response data
    response_data = []
    for face_feature in created_face_features:
        features_array = np.frombuffer(face_feature.features, dtype=np.float64)
        response_data.append({
            'id': face_feature.id,
            'features': features_array.tolist()[0],
            'asset_id': face_feature.asset_id,
            'url': face_feature.url,
            'created_at': face_feature.created_at.isoformat(),
            'pid': face_feature.pid
        })

    # Asynchronously call the function to insert unique faces
    await asyncio.to_thread(UniqueFace.insert_unique_face, created_face_features, pid)
    
    return jsonify({'message': 'Face features created', 'files': response_data}), 201

# Route to retrieve a single face feature by its ID
@facefeature_bp.route("/<int:id>", methods=['GET'])
def get_face_feature(id):
    face_feature = FaceFeature.get_face_feature_by_id(id)
    if not face_feature:
        return jsonify({'error': 'Face feature not found'}), 404

    features_array = np.frombuffer(face_feature.features, dtype=np.float64)
    return jsonify({
            'id': face_feature.id,
            'features': features_array.tolist()[0],
            'asset_id': face_feature.asset_id,
            'url': face_feature.url,
            'created_at': face_feature.created_at.isoformat(),
            'pid': face_feature.pid
        }), 200

# Route to retrieve all face features by a specific PID
@facefeature_bp.route("/pid/<int:pid>", methods=['GET'])
def get_face_features_by_pid(pid):
    face_features = FaceFeature.get_face_features_by_pid(pid)
    if not face_features:
        return jsonify({'error': 'No face features found for this PID'}), 404

    # Prepare the response data for each face feature
    response_data = []
    for face_feature in face_features:
        features_array = np.frombuffer(face_feature.features, dtype=np.float64)
        response_data.append({
            'id': face_feature.id,
            'features': features_array.tolist()[0],
            'asset_id': face_feature.asset_id,
            'url': face_feature.url,
            'created_at': face_feature.created_at.isoformat(),
            'pid': face_feature.pid
        })

    return jsonify(response_data), 200

# Route to update a face feature by ID
@facefeature_bp.route("/<int:id>", methods=['PATCH'])
def update_face_feature(id):
    face_feature = FaceFeature.get_face_feature_by_id(id)
    if not face_feature:
        return jsonify({'error': 'Face feature not found'}), 404

    data = request.json
    if 'pid' in data:
        face_feature.pid = data['pid']

    db.session.commit()  # Commit changes to the database

    return jsonify({'message': 'Face feature updated'}), 200

# Route to delete a face feature by ID
@facefeature_bp.route("/<int:id>", methods=['DELETE'])
def delete_face_feature(id):
    if not FaceFeature.delete_face_feature(id):
        return jsonify({'error': 'Face feature not found'}), 404

    return jsonify({'message': 'Face feature deleted'}), 200

# Route to find face matches based on uploaded or specified image
@facefeature_bp.route("/facefinder/<int:pid>", methods=['POST'])
def facefinder(pid):
    # Check for an image file or path in the request
    if 'image' not in request.files and 'path' not in request.form:
        return jsonify({'error': 'No image file or path provided'}), 400

    face_service = FaceRecognitionService()
    
    # Save uploaded image or use specified path
    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['FIND_FOLDER'], filename)
        os.makedirs(current_app.config['FIND_FOLDER'], exist_ok=True)
        file.save(filepath)
    else:
        filepath = request.form['path']

    # Process the image to extract face features
    features = face_service.process_image2(file)

    if features is None:
        return jsonify({'message': 'No faces found in image'}), 404

    # Find matching images for the extracted features
    response_data=[]
    matching_images = FaceFeature.find_matches(features, pid)
    # matching_images_list = [image.to_dict() for image in matching_images]
    for face_feature in matching_images:
        features_array = np.frombuffer(face_feature.features, dtype=np.float64)
        response_data.append({
            'id': face_feature.id,
            'features': features_array.tolist()[0],
            'asset_id': face_feature.asset_id,
            'url': face_feature.url,
            'created_at': face_feature.created_at.isoformat(),
            'pid': face_feature.pid
        })
    if matching_images:
        return jsonify({'matching_images': response_data}), 200
    else:
        return jsonify({'message': 'No matching images found'}), 404

# Route to serve uploaded image files
@facefeature_bp.route('/images/<path:filename>', methods=['GET'])
def get_uploaded_file(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    print(f"Serving file from: {upload_folder}/{filename}")
    try:
        # Serve the file from the specified upload directory
        return send_from_directory(os.getcwd(), filename)
    except FileNotFoundError:
        abort(404)  # Return 404 if the file is not found

@facefeature_bp.route('/listimages', methods=['GET'])
def list_uploaded_files():
    """List all images uploaded to Cloudinary with pagination."""
    cloud = CloudinaryUtil()
    upload_folder = current_app.config.get('UPLOAD_FOLDER')

    # Get pagination parameters from query string, with default values
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    next_cursor = request.args.get('next_cursor')

    try:
        # Fetch resources from Cloudinary using the CloudinaryUtil class
        if cloud:
            resources_data = cloud.list_resources(page=page, page_size=page_size,next_cursor=next_cursor)

            if 'error' in resources_data:
                # Handle errors from Cloudinary
                return jsonify({'error': resources_data['error']}), 500

            # Extract file list and pagination info
            file_list = resources_data['files']
            pagination_info = resources_data['pagination']

            return jsonify({
                'files': file_list,
                'pagination': pagination_info
            }), 200

        else:
            # Fallback to listing files from the local upload folder
            files = os.listdir(upload_folder)
            # Filter out directories, only include files
            file_list = [file for file in files if os.path.isfile(os.path.join(upload_folder, file))]
            return jsonify({'files': file_list}), 200

    except Exception as e:
        # Handle any unexpected exceptions
        return jsonify({'error': 'An unexpected error occurred: ' + str(e)}), 500