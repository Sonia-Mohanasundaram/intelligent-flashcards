"""Flashcard routes"""

from flask import Blueprint, request, jsonify
from middleware.jwt_handler import token_required
from models.note import Note
from models.flashcard import Flashcard
from services.ai_pipeline_17steps import AIProcessingPipeline
from utils.database import get_db
from io import BytesIO
import logging
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)
flashcard_bp = Blueprint('flashcards', __name__)


def _extract_text_from_upload(uploaded_file) -> str:
    filename = (uploaded_file.filename or '').lower()
    data = uploaded_file.read()
    
    if filename.endswith('.txt'):
        return data.decode('utf-8', errors='ignore')
    
    if filename.endswith('.pdf'):
        text_parts = []
        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or '')
        return '\n'.join(text_parts)
    
    if filename.endswith('.docx'):
        document = Document(BytesIO(data))
        return '\n'.join(paragraph.text for paragraph in document.paragraphs)
    
    raise ValueError('Supported files: TXT, PDF, DOCX')


@flashcard_bp.route('/generate', methods=['POST'])
@token_required
def generate_flashcards():
    """Generate flashcards from notes using AI"""
    try:
        data = request.get_json(silent=True) if request.is_json else None
        
        if request.files:
            uploaded_file = request.files.get('file')
            if not uploaded_file:
                return jsonify({'error': 'No file provided'}), 400
            text = _extract_text_from_upload(uploaded_file).strip()
            title = request.form.get('title') or uploaded_file.filename or 'Uploaded Notes'
        else:
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            text = data.get('text', '').strip()
            title = data.get('title', 'Untitled Notes').strip()
        
        if not text or len(text) < 40:
            return jsonify({'error': 'Please provide at least 40 characters of text'}), 400
        
        db = get_db()
        
        # Process with 17-step AI pipeline
        pipeline = AIProcessingPipeline()
        ai_result = pipeline.process(text, title)
        
        if not ai_result.get('success'):
            return jsonify({'error': ai_result.get('error', 'Processing failed')}), 500
        
        # Extract results
        pipeline_steps = ai_result.get('pipeline', {})
        flashcards_data = ai_result.get('flashcards', [])
        
        # Create note record
        note = Note.create(
            db,
            request.user_id,
            title,
            ai_result.get('topic', ai_result.get('subject', 'General Knowledge')),
            ai_result.get('topics', []),
            text,
            ai_result.get('summary', []),
            ai_result
        )
        
        # Create flashcard records
        flashcards = []
        for fc_data in flashcards_data:
            flashcard = Flashcard.create(
                db,
                request.user_id,
                note['_id'],
                fc_data['question'],
                fc_data['answer'],
                fc_data['difficulty'],
                fc_data['confidence'],
                fc_data.get('topic', ai_result.get('topic', ai_result.get('subject', 'General Knowledge'))),
                ai_result.get('topic', ai_result.get('subject', 'General Knowledge')),
                fc_data
            )
            flashcards.append(flashcard)
        
        db.history.insert_one({
            'userId': note['userId'],
            'noteId': note['_id'],
            'action': 'generated_flashcards',
            'title': title,
            'questionCount': len(flashcards),
            'createdAt': note['createdAt']
        })
        
        return jsonify({
            'message': 'Flashcards generated successfully',
            'note': note,
            'pipelineSteps': pipeline_steps,
            'pipelineTimeline': ai_result.get('pipelineTimeline', []),
            'summary': ai_result.get('summary', []),
            'topic': ai_result.get('topic', ai_result.get('subject', 'General Knowledge')),
            'subject': ai_result.get('topic', ai_result.get('subject', 'General Knowledge')),
            'confidence': ai_result.get('confidence', 0),
            'difficulty': ai_result.get('difficulty', 'Medium'),
            'readingLevel': ai_result.get('readingLevel', 'High School'),
            'studyTime': ai_result.get('studyTime', '0 min'),
            'readingTime': ai_result.get('readingTime', 0),
            'wordCount': ai_result.get('wordCount', 0),
            'questionCount': len(flashcards),
            'keywords': ai_result.get('keywords', []),
            'entities': ai_result.get('entities', []),
            'topics': ai_result.get('topics', []),
            'characterCount': ai_result.get('characterCount', 0),
            'cardCount': len(flashcards),
            'flashcards': flashcards
        }), 201
        
    except Exception as e:
        logger.error(f"Generate flashcards error: {str(e)}")
        return jsonify({'error': 'Failed to generate flashcards'}), 500


@flashcard_bp.route('/flashcards', methods=['GET'])
@token_required
def get_flashcards():
    """Get user's flashcards"""
    try:
        db = get_db()
        
        # Query parameters
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 50, type=int)
        difficulty = request.args.get('difficulty', None)
        known = request.args.get('known', None)
        favorite = request.args.get('favorite', None)
        
        # Convert string to boolean
        filters = {}
        if difficulty:
            filters['difficulty'] = difficulty
        if known is not None:
            filters['known'] = known.lower() == 'true'
        if favorite is not None:
            filters['favorite'] = favorite.lower() == 'true'
        
        cards = Flashcard.get_by_user(db, request.user_id, skip, limit, filters)
        stats = Flashcard.get_stats(db, request.user_id)
        
        return jsonify({
            'flashcards': cards,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Get flashcards error: {str(e)}")
        return jsonify({'error': 'Failed to fetch flashcards'}), 500


@flashcard_bp.route('/flashcards/<flashcard_id>', methods=['GET'])
@token_required
def get_flashcard(flashcard_id):
    """Get single flashcard"""
    try:
        db = get_db()
        card = Flashcard.get_by_id(db, flashcard_id, request.user_id)
        
        if not card:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        return jsonify({'flashcard': card}), 200
        
    except Exception as e:
        logger.error(f"Get flashcard error: {str(e)}")
        return jsonify({'error': 'Failed to fetch flashcard'}), 500


@flashcard_bp.route('/flashcards/<flashcard_id>/known', methods=['PUT'])
@token_required
def mark_known(flashcard_id):
    """Mark flashcard as known"""
    try:
        data = request.get_json() or {}
        known = data.get('known', False)
        
        db = get_db()
        card = Flashcard.mark_known(db, flashcard_id, request.user_id, known)
        
        if not card:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        return jsonify({
            'message': f'Flashcard marked as {"known" if known else "not known"}',
            'flashcard': card
        }), 200
        
    except Exception as e:
        logger.error(f"Mark known error: {str(e)}")
        return jsonify({'error': 'Failed to update flashcard'}), 500


@flashcard_bp.route('/flashcards/<flashcard_id>/favorite', methods=['POST'])
@token_required
def add_favorite(flashcard_id):
    """Add flashcard to favorites"""
    try:
        db = get_db()
        card = Flashcard.add_to_favorite(db, flashcard_id, request.user_id)
        
        if not card:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        return jsonify({
            'message': 'Added to favorites',
            'flashcard': card
        }), 200
        
    except Exception as e:
        logger.error(f"Add favorite error: {str(e)}")
        return jsonify({'error': 'Failed to add to favorites'}), 500


@flashcard_bp.route('/flashcards/<flashcard_id>/favorite', methods=['DELETE'])
@token_required
def remove_favorite(flashcard_id):
    """Remove flashcard from favorites"""
    try:
        db = get_db()
        card = Flashcard.remove_from_favorite(db, flashcard_id, request.user_id)
        
        if not card:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        return jsonify({
            'message': 'Removed from favorites',
            'flashcard': card
        }), 200
        
    except Exception as e:
        logger.error(f"Remove favorite error: {str(e)}")
        return jsonify({'error': 'Failed to remove from favorites'}), 500


@flashcard_bp.route('/flashcards/<flashcard_id>', methods=['DELETE'])
@token_required
def delete_flashcard(flashcard_id):
    """Delete flashcard"""
    try:
        db = get_db()
        success = Flashcard.delete(db, flashcard_id, request.user_id)
        
        if not success:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        return jsonify({'message': 'Flashcard deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete flashcard error: {str(e)}")
        return jsonify({'error': 'Failed to delete flashcard'}), 500


@flashcard_bp.route('/favorites', methods=['GET'])
@token_required
def get_favorites():
    """Get favorite flashcards"""
    try:
        db = get_db()
        
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        filters = {'favorite': True}
        cards = Flashcard.get_by_user(db, request.user_id, skip, limit, filters)
        
        return jsonify({'favorites': cards}), 200
        
    except Exception as e:
        logger.error(f"Get favorites error: {str(e)}")
        return jsonify({'error': 'Failed to fetch favorites'}), 500
