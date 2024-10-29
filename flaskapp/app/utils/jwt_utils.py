import jwt  # Avoids conflict by renaming PyJWT import
from datetime import datetime, timedelta, timezone
from flask import current_app, request, jsonify  # Add request here
from app.models.user import User  
import pytz

from functools import wraps



def generate_token(user_id, expires_in=3600):
    """Generate a JWT token for a given user."""
    # Define the Indian time zone
    indian_tz = pytz.timezone('Asia/Kolkata')
    # Get the current time in Indian time zone
    now_ist = datetime.now(indian_tz)
    try:
        payload = {
            'user_id': user_id,
            'exp': now_ist + timedelta(seconds=expires_in)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token if isinstance(token, str) else token.decode('utf-8')
    except Exception as e:
        print(f"Error generating token: {e}")
        return None

def decode_token(token):
    """Decode and validate the JWT token."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        return User.query.get(user_id)
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None

def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401

        # Extract token part after "Bearer "
        try:
            token = token.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Invalid token format'}), 401

        # Decode the token to get the user
        user = decode_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Attach the user to the request context
        request.user = user
        return f(*args, **kwargs)
    return decorated_function

