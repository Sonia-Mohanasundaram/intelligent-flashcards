"""Utility functions"""

import logging
from functools import wraps
from flask import jsonify, request

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )


def validate_request_json(f):
    """Decorator to validate that request has JSON data"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        return f(*args, **kwargs)
    return decorated


def paginate(skip: int = 0, limit: int = 50) -> dict:
    """Get pagination parameters"""
    return {
        'skip': max(0, skip),
        'limit': max(1, min(limit, 100))  # Max 100 per page
    }
