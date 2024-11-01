from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.jwt_utils import generate_token, authorize
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)

# Sign Up Route
@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.signup(email, password)
    if user:
        token = generate_token(user.user_id)
        return jsonify({'message': 'User registered successfully', 'token': token}), 201
    else:
        return jsonify({'error': 'Email already exists or an error occurred'}), 400

# Login Route
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.login(email, password)
    if user:
        if user.delete_at:
            return jsonify({'error': 'Account has been deactivated'}), 403

        token = generate_token(user.user_id)
        return jsonify({'message': 'Login successful', 'token': token}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

# Get User Profile
@user_bp.route('/profile', methods=['GET'])
@authorize
def get_profile():
    user = request.user
    return jsonify({
        'user_id': user.user_id,
        'email': user.email,
        'created_at': user.created_at,
        'delete_at': user.delete_at
    }), 200

# Update User
@user_bp.route('/update', methods=['PUT'])
@authorize
def update_user():
    user = request.user
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    updated_user = User.update(
        user_id=user.user_id,
        email=email,
        password=password
    )

    if updated_user:
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'error': 'Error updating user'}), 500

# Deactivate User (Soft Delete)
@user_bp.route('/deactivate', methods=['DELETE'])
@authorize
def deactivate_user():
    user = request.user

    if User.deactivate_user(user.user_id):
        return jsonify({'message': 'User account deactivated successfully'}), 200
    else:
        return jsonify({'error': 'Error deactivating user'}), 500

#DELETE user by Id
@user_bp.route('/permanentdelete', methods=['DELETE'])
@authorize
def delete_user():
    user = request.user

    if User.delete_user(user.user_id):
        return jsonify({'message': 'User account deleted successfully'}), 200
    else:
        return jsonify({'error': 'Error deactivating user'}), 500
