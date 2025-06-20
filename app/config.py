import os

SECRET_KEY = 'secret-key'

# SQLALCHEMY_DATABASE_URI = 'localhost'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://tsoy:password@localhost/tsoy_exam'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..',
    'media', 
    'images'
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

ANIMALS_PER_PAGE = 10