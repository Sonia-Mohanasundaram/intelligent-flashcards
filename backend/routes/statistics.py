"""Statistics routes"""

from flask import Blueprint, request, jsonify
from middleware.jwt_handler import token_required
from services.statistics import StatisticsService
from utils.database import get_db
import logging

logger = logging.getLogger(__name__)
statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/statistics', methods=['GET'])
@token_required
def get_statistics():
    """Get user statistics"""
    try:
        stats = StatisticsService.get_dashboard_stats(get_db(), request.user_id)
        
        return jsonify({
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Get statistics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500


@statistics_bp.route('/statistics/subject/<subject>', methods=['GET'])
@token_required
def get_subject_statistics(subject):
    """Get statistics for a specific subject"""
    try:
        stats = StatisticsService.get_subject_stats(get_db(), request.user_id, subject)
        
        if not stats:
            return jsonify({'error': 'No data for this subject'}), 404
        
        return jsonify({
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Get subject statistics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch subject statistics'}), 500
