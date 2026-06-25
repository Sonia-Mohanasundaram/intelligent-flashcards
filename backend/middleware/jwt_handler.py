"""JWT Authentication Middleware"""

import jwt
import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from config import Config
from bson import ObjectId

logger = logging.getLogger(__name__)


def generate_token(user_id: str) -> str:
    """
    Generate JWT token for user
    
    Args:
        user_id: MongoDB ObjectId as string
    
    Returns:
        JWT token
    """
    try:
        payload = {
            'user_id': str(user_id),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + Config.JWT_EXPIRATION
        }
        
        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM
        )
        return token
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise


def verify_token(token: str) -> dict:
    """
    Verify JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise jwt.InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise


def token_required(f):
    """
    Decorator to protect routes requiring authentication
    
    Usage:
        @app.route('/api/profile')
        @token_required
        def get_profile():
            user_id = request.user_id
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid Authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = verify_token(token)
            request.user_id = payload['user_id']
            return f(*args, **kwargs)
        except jwt.InvalidTokenError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated


def get_token_from_request():
    """
    Extract token from request header
    
    Returns:
        Token string or None
    """
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            return auth_header.split(" ")[1]
        except IndexError:
            return None
    return None
