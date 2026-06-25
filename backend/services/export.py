"""Export services for JSON, CSV, and PDF formats"""

import json
import csv
import io
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting data in various formats"""
    
    @staticmethod
    def export_json(db, user_id: str, note_id: str = None) -> dict:
        """Export flashcards as JSON"""
        try:
            user_oid = ObjectId(user_id)
            query = {'userId': user_oid}
            
            if note_id:
                query['noteId'] = ObjectId(note_id)
            
            cards = list(db.flashcards.find(query))
            
            # Convert ObjectId to strings for JSON serialization
            export_data = {
                'exportDate': datetime.utcnow().isoformat(),
                'flashcards': []
            }
            
            for card in cards:
                card['_id'] = str(card['_id'])
                card['userId'] = str(card['userId'])
                card['noteId'] = str(card['noteId'])
                export_data['flashcards'].append(card)
            
            return export_data
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def export_csv(db, user_id: str, note_id: str = None) -> str:
        """Export flashcards as CSV"""
        try:
            user_oid = ObjectId(user_id)
            query = {'userId': user_oid}
            
            if note_id:
                query['noteId'] = ObjectId(note_id)
            
            cards = list(db.flashcards.find(query))
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Question',
                'Answer',
                'Difficulty',
                'Topic',
                'Confidence',
                'Known',
                'Favorite',
                'Created'
            ])
            
            # Write data
            for card in cards:
                writer.writerow([
                    card.get('question', ''),
                    card.get('answer', ''),
                    card.get('difficulty', ''),
                    card.get('topic', ''),
                    card.get('confidence', ''),
                    card.get('known', False),
                    card.get('favorite', False),
                    card.get('createdAt', '').isoformat() if isinstance(card.get('createdAt'), datetime) else ''
                ])
            
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return f"Error: {str(e)}"
    
    @staticmethod
    def export_pdf_data(db, user_id: str, note_id: str = None) -> dict:
        """Prepare data for PDF export"""
        try:
            user_oid = ObjectId(user_id)
            query = {'userId': user_oid}
            
            if note_id:
                query['noteId'] = ObjectId(note_id)
                note = db.notes.find_one({'_id': ObjectId(note_id)})
                note_title = note['title'] if note else "Flashcards"
            else:
                note_title = "All Flashcards"
            
            cards = list(db.flashcards.find(query).sort('createdAt', -1))
            
            # Group by topic
            by_topic = {}
            for card in cards:
                topic = card.get('topic', 'General')
                if topic not in by_topic:
                    by_topic[topic] = []
                by_topic[topic].append(card)
            
            return {
                'title': note_title,
                'exportDate': datetime.utcnow().isoformat(),
                'totalCards': len(cards),
                'byTopic': by_topic,
                'summary': {
                    'easy': sum(1 for c in cards if c.get('difficulty') == 'Easy'),
                    'medium': sum(1 for c in cards if c.get('difficulty') == 'Medium'),
                    'hard': sum(1 for c in cards if c.get('difficulty') == 'Hard'),
                    'known': sum(1 for c in cards if c.get('known')),
                    'favorite': sum(1 for c in cards if c.get('favorite'))
                }
            }
        except Exception as e:
            logger.error(f"Error preparing PDF data: {str(e)}")
            return {'error': str(e)}
