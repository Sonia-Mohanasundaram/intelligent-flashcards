"""Authentication routes (signup, login, profile)"""

from flask import Blueprint, request, jsonify
from middleware.jwt_handler import generate_token, token_required
from models.user import User
from utils.database import get_db
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        
        # Validation
        if not email or '@' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if not name or len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters'}), 400
        
        db = get_db()
        
        # Create user
        user = User.create(db, email, password, name)
        
        # Generate token
        token = generate_token(user['_id'])
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user['_id'],
                'email': user['email'],
                'name': user['name']
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        db = get_db()
        
        # Verify password
        if not User.verify_password(db, email, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Get user
        user = User.find_by_email(db, email)
        
        # Generate token
        token = generate_token(user['_id'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['_id'],
                'email': user['email'],
                'name': user['name']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    try:
        db = get_db()
        user = User.find_by_id(db, request.user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['_id'],
                'email': user['email'],
                'name': user['name'],
                'createdAt': user.get('createdAt', '').isoformat() if isinstance(user.get('createdAt'), type(user.get('createdAt'))) else ''
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to fetch profile'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile (only name)"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        name = data.get('name', '').strip()
        
        if not name or len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters'}), 400
        
        db = get_db()
        user = User.update_profile(db, request.user_id, name=name)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user['_id'],
                'email': user['email'],
                'name': user['name']
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500


@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        old_password = data.get('oldPassword', '').strip()
        new_password = data.get('newPassword', '').strip()
        
        if not old_password or not new_password:
            return jsonify({'error': 'Both passwords required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        if old_password == new_password:
            return jsonify({'error': 'New password must be different'}), 400
        
        db = get_db()
        User.change_password(db, request.user_id, old_password, new_password)
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500
