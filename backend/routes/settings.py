"""Settings routes"""

from flask import Blueprint, request, jsonify
from middleware.jwt_handler import token_required
from models.user import User
from utils.database import get_db
import logging

logger = logging.getLogger(__name__)
settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET'])
@token_required
def get_settings():
    """Get user settings"""
    try:
        db = get_db()
        user = User.find_by_id(db, request.user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'settings': {
                'fullName': user.get('name', ''),
                'email': user.get('email', ''),
                'createdAt': user.get('createdAt', '').isoformat() if hasattr(user.get('createdAt', ''), 'isoformat') else str(user.get('createdAt', ''))
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get settings error: {str(e)}")
        return jsonify({'error': 'Failed to fetch settings'}), 500


@settings_bp.route('/settings', methods=['PUT'])
@token_required
def update_settings():
    """Update user settings (only name)"""
    try:
        data = request.get_json()
        
        if not data or 'fullName' not in data:
            return jsonify({'error': 'Full name is required'}), 400
        
        full_name = data.get('fullName', '').strip()
        
        if not full_name or len(full_name) < 2:
            return jsonify({'error': 'Full name must be at least 2 characters'}), 400
        
        db = get_db()
        user = User.update_profile(db, request.user_id, name=full_name)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'Settings updated successfully',
            'settings': {
                'fullName': user.get('name', ''),
                'email': user.get('email', '')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Update settings error: {str(e)}")
        return jsonify({'error': 'Failed to update settings'}), 500
