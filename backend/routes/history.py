"""History routes"""

from flask import Blueprint, request, jsonify
from middleware.jwt_handler import token_required
from models.note import Note
from utils.database import get_db
import logging

logger = logging.getLogger(__name__)
history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
@token_required
def get_history():
    """Get user's note history"""
    try:
        db = get_db()
        
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 50, type=int)
        search = request.args.get('search', None)
        topic = request.args.get('topic', None)
        subject = request.args.get('subject', None)

        notes = Note.get_by_user(db, request.user_id, skip, limit, search, topic, subject)
        
        return jsonify({'history': notes}), 200
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return jsonify({'error': 'Failed to fetch history'}), 500


@history_bp.route('/history/<note_id>', methods=['GET'])
@token_required
def get_history_item(note_id):
    """Get specific note from history"""
    try:
        db = get_db()
        note = Note.get_by_id(db, note_id, request.user_id)
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        return jsonify({'note': note}), 200
        
    except Exception as e:
        logger.error(f"Get history item error: {str(e)}")
        return jsonify({'error': 'Failed to fetch note'}), 500


@history_bp.route('/history/<note_id>', methods=['PUT'])
@token_required
def update_history_item(note_id):
    """Update note (rename)"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        title = data.get('title', '').strip()
        
        if not title or len(title) < 2:
            return jsonify({'error': 'Title must be at least 2 characters'}), 400
        
        db = get_db()
        note = Note.update(db, note_id, request.user_id, title=title)
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        return jsonify({
            'message': 'Note updated successfully',
            'note': note
        }), 200
        
    except Exception as e:
        logger.error(f"Update history item error: {str(e)}")
        return jsonify({'error': 'Failed to update note'}), 500


@history_bp.route('/history/<note_id>', methods=['DELETE'])
@token_required
def delete_history_item(note_id):
    """Delete note and associated flashcards"""
    try:
        db = get_db()
        success = Note.delete(db, note_id, request.user_id)
        
        if not success:
            return jsonify({'error': 'Note not found'}), 404
        
        return jsonify({'message': 'Note deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete history item error: {str(e)}")
        return jsonify({'error': 'Failed to delete note'}), 500


@history_bp.route('/history/subjects', methods=['GET'])
@token_required
def get_subjects():
    """Get all unique subjects"""
    try:
        db = get_db()
        subjects = Note.get_all_subjects(db, request.user_id)
        
        return jsonify({'subjects': subjects}), 200
        
    except Exception as e:
        logger.error(f"Get subjects error: {str(e)}")
        return jsonify({'error': 'Failed to fetch subjects'}), 500


@history_bp.route('/history/topics', methods=['GET'])
@token_required
def get_topics():
    """Get all unique topics"""
    try:
        db = get_db()
        topics = Note.get_all_topics(db, request.user_id)
        
        return jsonify({'topics': topics}), 200
        
    except Exception as e:
        logger.error(f"Get topics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch topics'}), 500
