import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env from the same directory as this config file
config_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(config_dir, '.env'))

class Config:
    """Base configuration"""
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/smartflashcard')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'smartflashcard')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION = timedelta(days=7)
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', True)
    
    # CORS
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    CORS_ORIGINS = [
        FRONTEND_URL,
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:8080',
        'http://localhost:8081',
        'http://127.0.0.1:8080',
        'http://127.0.0.1:8081',
        'http://localhost:5000',
    ]
    
    # Server
    SERVER_PORT = int(os.getenv('SERVER_PORT', os.getenv('PORT', 5000)))
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    
    # AI Models
    SPACY_MODEL = 'en_core_web_sm'
    SUMMARIZATION_MODEL = 't5-small'
    QUESTION_GENERATION_MODEL = 'deepset/deberta-v3-small-squad2'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGODB_DB_NAME = 'smartflashcard_test'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
