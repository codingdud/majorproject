from flask import Blueprint, request, jsonify
from app.models.project import Project
from app.utils.jwt_utils import authorize

project_bp = Blueprint('project', __name__)

# Create a new project
@project_bp.route('/create', methods=['POST'])
@authorize
def create_project():
    user = request.user
    user_id = user.user_id
    data = request.get_json()
    p_name = data.get('p_name')
    thumb_nail = data.get('thumb_nail', '/default/placeholder.png')

    if not p_name:
        return jsonify({'error': 'project name are required'}), 400

    new_project = Project.create_project(user_id, p_name, thumb_nail)
    return jsonify({'message': 'Project created successfully', 'project_id': new_project.pid}), 201

# Get all projects
@project_bp.route('/getall', methods=['GET'])
def get_projects():
    projects = Project.get_all_projects()
    return jsonify([{'pid': p.pid, 'user_id': p.user_id, 'p_name': p.p_name, 'thumb_nail': p.thumb_nail} for p in projects]), 200

# Get a project by ID
@project_bp.route('/<int:pid>', methods=['GET'])
def get_project(pid):
    project = Project.get_project_by_id(pid)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify({'pid': project.pid, 'user_id': project.user_id, 'p_name': project.p_name, 'thumb_nail': project.thumb_nail}), 200

# Get projects by user_id
@project_bp.route('/user', methods=['GET'])
@authorize
def get_projects_by_user():
    user = request.user
    user_id = user.user_id
    projects = Project.get_projects_by_user_id(user_id)
    return jsonify([{'pid': p.pid, 'p_name': p.p_name, 'thumb_nail': p.thumb_nail} for p in projects]), 200

# Update a project
@project_bp.route('/<int:pid>', methods=['PUT'])
def update_project(pid):
    data = request.get_json()
    p_name = data.get('p_name')
    thumb_nail = data.get('thumb_nail')

    project = Project.update_project(pid, p_name, thumb_nail)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify({'message': 'Project updated successfully'}), 200

# Delete a project
@project_bp.route('/<int:pid>', methods=['DELETE'])
def delete_project(pid):
    if Project.delete_project(pid):
        return jsonify({'message': 'Project deleted successfully'}), 200
    return jsonify({'error': 'Project not found'}), 404
