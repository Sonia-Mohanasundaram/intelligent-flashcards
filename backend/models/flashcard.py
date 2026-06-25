"""Flashcard model and database operations"""

from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class Flashcard:
    """Flashcard model"""
    
    @staticmethod
    def create(db, user_id: str, note_id: str, question: str, answer: str, 
               difficulty: str, confidence: int, topic: str = "", subject: str = "",
               metadata: dict = None) -> dict:
        """
        Create new flashcard
        
        Args:
            db: MongoDB database instance
            user_id: User ID
            note_id: Note ID
            question: Question text
            answer: Answer text
            difficulty: Difficulty level (Easy, Medium, Hard)
            confidence: AI confidence score (0-100)
            topic: Primary topic tag
            subject: Optional subject alias for compatibility
        
        Returns:
            Flashcard document
        """
        subject = subject or topic
        flashcard_doc = {
            'userId': ObjectId(user_id),
            'noteId': ObjectId(note_id),
            'question': question,
            'answer': answer,
            'difficulty': difficulty,
            'confidence': confidence,
            'topic': topic,
            'subject': subject,
            'known': False,
            'favorite': False,
            'revisionStatus': 'new',
            'revisionPriority': (metadata or {}).get('revisionPriority', 'low'),
            'reviewCount': 0,
            'lastReviewedAt': None,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        if metadata:
            flashcard_doc.update({
                'type': metadata.get('type', ''),
                'keyword': metadata.get('keyword', ''),
                'sourceSentence': metadata.get('sourceSentence', ''),
                'sentenceImportance': metadata.get('sentenceImportance', 0),
                'keywordRelevance': metadata.get('keywordRelevance', 0),
                'entityRelevance': metadata.get('entityRelevance', 0),
                'revisionStatus': metadata.get('revisionStatus', 'new'),
            })
        
        result = db.flashcards.insert_one(flashcard_doc)
        flashcard_doc['_id'] = str(result.inserted_id)
        flashcard_doc['userId'] = user_id
        flashcard_doc['noteId'] = note_id
        
        return flashcard_doc
    
    @staticmethod
    def get_by_user(db, user_id: str, skip: int = 0, limit: int = 50, 
                    filters: dict = None) -> list:
        """Get user's flashcards with optional filters"""
        query = {'userId': ObjectId(user_id)}
        
        if filters:
            if 'difficulty' in filters and filters['difficulty']:
                query['difficulty'] = filters['difficulty']
            if 'known' in filters:
                query['known'] = filters['known']
            if 'favorite' in filters:
                query['favorite'] = filters['favorite']
            if 'subject' in filters and filters['subject']:
                query['subject'] = filters['subject']
            if 'topic' in filters and filters['topic']:
                query['topic'] = filters['topic']
        
        cards = list(db.flashcards.find(query)
                     .sort('createdAt', -1)
                     .skip(skip)
                     .limit(limit))
        
        for card in cards:
            card['_id'] = str(card['_id'])
            card['userId'] = user_id
            card['noteId'] = str(card['noteId'])
        
        return cards
    
    @staticmethod
    def get_by_id(db, flashcard_id: str, user_id: str = None) -> dict:
        """Get flashcard by ID"""
        try:
            query = {'_id': ObjectId(flashcard_id)}
            if user_id:
                query['userId'] = ObjectId(user_id)
            
            card = db.flashcards.find_one(query)
            if card:
                card['_id'] = str(card['_id'])
                card['userId'] = str(card['userId'])
                card['noteId'] = str(card['noteId'])
            return card
        except Exception as e:
            logger.error(f"Error finding flashcard: {str(e)}")
            return None
    
    @staticmethod
    def mark_known(db, flashcard_id: str, user_id: str, known: bool) -> dict:
        """Mark flashcard as known/not known"""
        try:
            card = db.flashcards.find_one_and_update(
                {'_id': ObjectId(flashcard_id), 'userId': ObjectId(user_id)},
                {
                    '$set': {
                        'known': known,
                        'updatedAt': datetime.utcnow(),
                        'lastReviewedAt': datetime.utcnow()
                    },
                    '$inc': {'reviewCount': 1}
                },
                return_document=True
            )
            
            if card:
                card['_id'] = str(card['_id'])
                card['userId'] = str(card['userId'])
                card['noteId'] = str(card['noteId'])
            
            return card
        except Exception as e:
            logger.error(f"Error marking card known: {str(e)}")
            return None
    
    @staticmethod
    def add_to_favorite(db, flashcard_id: str, user_id: str) -> dict:
        """Add flashcard to favorites"""
        try:
            card = db.flashcards.find_one_and_update(
                {'_id': ObjectId(flashcard_id), 'userId': ObjectId(user_id)},
                {'$set': {'favorite': True, 'updatedAt': datetime.utcnow()}},
                return_document=True
            )
            
            if card:
                card['_id'] = str(card['_id'])
                card['userId'] = str(card['userId'])
                card['noteId'] = str(card['noteId'])
            
            return card
        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return None
    
    @staticmethod
    def remove_from_favorite(db, flashcard_id: str, user_id: str) -> dict:
        """Remove flashcard from favorites"""
        try:
            card = db.flashcards.find_one_and_update(
                {'_id': ObjectId(flashcard_id), 'userId': ObjectId(user_id)},
                {'$set': {'favorite': False, 'updatedAt': datetime.utcnow()}},
                return_document=True
            )
            
            if card:
                card['_id'] = str(card['_id'])
                card['userId'] = str(card['userId'])
                card['noteId'] = str(card['noteId'])
            
            return card
        except Exception as e:
            logger.error(f"Error removing from favorites: {str(e)}")
            return None
    
    @staticmethod
    def delete(db, flashcard_id: str, user_id: str) -> bool:
        """Delete flashcard"""
        try:
            result = db.flashcards.delete_one({
                '_id': ObjectId(flashcard_id),
                'userId': ObjectId(user_id)
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting flashcard: {str(e)}")
            return False
    
    @staticmethod
    def get_stats(db, user_id: str) -> dict:
        """Get flashcard statistics for user"""
        try:
            user_oid = ObjectId(user_id)
            total = db.flashcards.count_documents({'userId': user_oid})
            known = db.flashcards.count_documents({'userId': user_oid, 'known': True})
            favorite = db.flashcards.count_documents({'userId': user_oid, 'favorite': True})
            
            # Count by difficulty
            easy = db.flashcards.count_documents({'userId': user_oid, 'difficulty': 'Easy'})
            medium = db.flashcards.count_documents({'userId': user_oid, 'difficulty': 'Medium'})
            hard = db.flashcards.count_documents({'userId': user_oid, 'difficulty': 'Hard'})
            
            # Average confidence
            avg_pipeline = [
                {'$match': {'userId': user_oid}},
                {'$group': {'_id': None, 'avgConfidence': {'$avg': '$confidence'}}}
            ]
            avg_result = list(db.flashcards.aggregate(avg_pipeline))
            avg_confidence = avg_result[0]['avgConfidence'] if avg_result else 0
            
            return {
                'total': total,
                'known': known,
                'notKnown': total - known,
                'favorite': favorite,
                'completion': round((known / total * 100) if total > 0 else 0, 2),
                'avgConfidence': round(avg_confidence, 2),
                'difficulty': {
                    'easy': easy,
                    'medium': medium,
                    'hard': hard
                }
            }
        except Exception as e:
            logger.error(f"Error getting flashcard stats: {str(e)}")
            return {}
