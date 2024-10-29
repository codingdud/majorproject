from flask import Blueprint, jsonify, request, abort
from app.database import db
from .models import UniqueFace  # Make sure the model import path is correct

unique_face_bp = Blueprint('unique_face', __name__, url_prefix='/unique_faces')

@unique_face_bp.route('/<int:pid>', methods=['GET'])
def get_faces_by_pid(pid):
    try:
        faces = UniqueFace.get_faces_by_pid(pid)
        faces_data = [{"uid": face.uid, "label": face.label, "image_paths": face.image_paths} for face in faces]
        return jsonify(faces_data)
    except Exception as e:
        print(e)
        abort(500, description="Error retrieving faces by PID")


@unique_face_bp.route('/update/<int:uid>', methods=['PUT'])
def update_unique_face(uid):
    updated_data = request.get_json()
    try:
        unique_face = UniqueFace.update_unique_face(uid, updated_data)
        if unique_face:
            return jsonify({"message": "Unique face updated successfully"}), 200
        else:
            abort(404, description="Unique face not found")
    except Exception as e:
        print(e)
        abort(500, description="Error updating unique face")


@unique_face_bp.route('/delete/<int:uid>', methods=['DELETE'])
def delete_unique_face(uid):
    try:
        if UniqueFace.delete_unique_face(uid):
            return jsonify({"message": "Unique face deleted successfully"}), 200
        else:
            abort(404, description="Unique face not found")
    except Exception as e:
        print(e)
        abort(500, description="Error deleting unique face")
