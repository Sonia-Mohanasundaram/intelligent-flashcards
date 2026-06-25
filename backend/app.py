"""Flask application factory"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from utils.database import init_db
from utils.helpers import setup_logging
from routes.auth import auth_bp
from routes.flashcards import flashcard_bp
from routes.history import history_bp
from routes.statistics import statistics_bp
from routes.export import export_bp
from routes.settings import settings_bp
import logging
import os

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Create and configure Flask application"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Setup logging
    setup_logging()
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup CORS
    CORS(
        app,
        origins=app.config.get('CORS_ORIGINS', ['*']),
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # Initialize database
    with app.app_context():
        init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(flashcard_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(statistics_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'ok',
            'message': 'Smart Flashcard AI Backend is running',
            'version': '1.0.0'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info(f"Flask app created with config: {config_name}")
    
    return app
