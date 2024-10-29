import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    POSTGRES_CONN_DETAILS = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'sslmode': os.getenv('POSTGRES_SSLMODE'),
        'sslrootcert': os.getenv('POSTGRES_SSLROOTCERT', 'ca.pem')
    }
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_CONN_DETAILS['user']}:{POSTGRES_CONN_DETAILS['password']}"
        f"@{POSTGRES_CONN_DETAILS['host']}:{POSTGRES_CONN_DETAILS['port']}"
        f"/{POSTGRES_CONN_DETAILS['dbname']}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Face Recognition Configuration
    FIND_FOLDER = os.getenv('FIND_FOLDER', 'find')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    DLIB_SHAPE_PREDICTOR = 'shape_predictor_68_face_landmarks.dat'
    DLIB_FACE_RECOGNITION = 'dlib_face_recognition_resnet_model_v1.dat'
    
    # Migration Configuration
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'facial_features.db')

    #Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')