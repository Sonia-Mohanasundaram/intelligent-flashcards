"""Export routes"""

from flask import Blueprint, request, jsonify, Response
from middleware.jwt_handler import token_required
from services.export import ExportService
from utils.database import get_db
import json
import logging

logger = logging.getLogger(__name__)
export_bp = Blueprint('export', __name__)


@export_bp.route('/export/json', methods=['GET'])
@token_required
def export_json():
    """Export flashcards as JSON"""
    try:
        note_id = request.args.get('noteId', None)
        
        data = ExportService.export_json(get_db(), request.user_id, note_id)
        
        if 'error' in data:
            return jsonify(data), 500
        
        return jsonify(data), 200
        
    except Exception as e:
        logger.error(f"Export JSON error: {str(e)}")
        return jsonify({'error': 'Failed to export data'}), 500


@export_bp.route('/export/csv', methods=['GET'])
@token_required
def export_csv():
    """Export flashcards as CSV"""
    try:
        note_id = request.args.get('noteId', None)
        
        csv_data = ExportService.export_csv(get_db(), request.user_id, note_id)
        
        if csv_data.startswith('Error:'):
            return jsonify({'error': csv_data}), 500
        
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=flashcards.csv'}
        ), 200
        
    except Exception as e:
        logger.error(f"Export CSV error: {str(e)}")
        return jsonify({'error': 'Failed to export data'}), 500


@export_bp.route('/export/pdf-data', methods=['GET'])
@token_required
def export_pdf_data():
    """Get data for PDF export (frontend handles PDF generation)"""
    try:
        note_id = request.args.get('noteId', None)
        
        data = ExportService.export_pdf_data(get_db(), request.user_id, note_id)
        
        if 'error' in data:
            return jsonify(data), 500
        
        return jsonify(data), 200
        
    except Exception as e:
        logger.error(f"Export PDF data error: {str(e)}")
        return jsonify({'error': 'Failed to prepare export data'}), 500
