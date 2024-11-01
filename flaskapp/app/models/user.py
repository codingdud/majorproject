from app.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)  # Automatically increments
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delete_at = db.Column(db.DateTime, nullable=True)
    
    # Define relationship with Project model
    projects = db.relationship('Project', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    # SIGNUP - Register a new user
    @classmethod
    def signup(cls, email, password):
        # Check if the email already exists
        if cls.query.filter_by(email=email).first():
            print("Email already registered.")
            return None
        
        try:
            hashed_password = generate_password_hash(password)
            new_user = cls(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            print(f"Error signing up user: {e}")
            return None

    # LOGIN - Authenticate a user
    @classmethod
    def login(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user and user.delete_at is None:  # Check if the user exists and is active
            if check_password_hash(user.password, password):
                print("Login successful.")
                return user
            else:
                print("Invalid password.")
                return None
        else:
            print("Invalid email or user is deactivated.")
            return None

    # GET user by ID (for example, to fetch profile data)
    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.get(user_id)

    # UPDATE user information
    @classmethod
    def update(cls,user_id,email=None, password=None, delete_at=None):
        """Updates user information in the database."""
        try:
            user=cls.query.get(user_id)
            if user:
                # Optionally check if email already exists
                if  email:
                    # Check if the email already exists for another user
                    existing_user = cls.query.filter(cls.email == email, cls.user_id != user_id).first()
                    if existing_user:
                        return False, "Email already in use by another user"
                    user.email = email
                if password:
                    user.password = generate_password_hash(password)  # Hash the new password
                if delete_at:
                    user.delete_at = datetime.utcnow()

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {e}")
            return None

    # deactivate user by ID
    @classmethod
    def deactivate_user(cls, user_id):
        user = cls.query.get(user_id)
        if not user:
            return False
        
        try:
            # Set the delete_at field to the current datetime
            user.delete_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error marking user as deleted: {e}")
            return False

    # GET all users with optional pagination
    @classmethod
    def get_all_users(cls, page=None, per_page=10):
        query = cls.query
        if page is not None:
            users = query.paginate(page=page, per_page=per_page, error_out=False).items
        else:
            users = query.all()
        return users
    
    @classmethod
    def delete_user(cls, user_id):
        """
        Permanently delete a user by ID.
        """
        user = cls.query.get(user_id)
        if not user:
            return False

        try:
            # Permanently delete the user from the database
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting user: {e}")
            return False
