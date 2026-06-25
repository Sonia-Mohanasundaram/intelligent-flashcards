"""Note model and database operations"""

from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class Note:
    """Note model"""
    
    @staticmethod
    def create(db, user_id: str, title: str, topic: str, topics: list,
               original_text: str, summary: list, ai_result: dict, subject: str = None) -> dict:
        """
        Create new note
        
        Args:
            db: MongoDB database instance
            user_id: User ID
            title: Note title
            topic: Primary note topic
            topics: List of topics
            original_text: Original note text
            summary: Summary bullet points
            ai_result: Full AI processing result
            subject: Optional subject alias for compatibility
        
        Returns:
            Note document
        """
        subject = subject or topic
        note_doc = {
            'userId': ObjectId(user_id),
            'title': title,
            'topic': topic,
            'subject': subject,
            'topics': topics,
            'originalText': original_text,
            'summary': summary,
            'keywords': ai_result.get('keywords', []),
            'entities': ai_result.get('entities', []),
            'confidence': ai_result.get('confidence', 0),
            'difficulty': ai_result.get('difficulty', 'Medium'),
            'readingTime': ai_result.get('readingTime', 0),
            'studyTime': ai_result.get('studyTime', 0),
            'wordCount': ai_result.get('wordCount', ai_result.get('totalWords', 0)),
            'characterCount': ai_result.get('characterCount', 0),
            'questionCount': ai_result.get('questionCount', ai_result.get('questionsGenerated', 0)),
            'cardCount': ai_result.get('cardCount', ai_result.get('questionCount', 0)),
            'readingLevel': ai_result.get('readingLevel', ''),
            'pipelineSteps': ai_result.get('pipeline', {}),
            'pipelineTimeline': ai_result.get('pipelineTimeline', []),
            'flashcards': ai_result.get('flashcards', []),
            'historyStatus': 'generated',
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = db.notes.insert_one(note_doc)
        note_doc['_id'] = str(result.inserted_id)
        note_doc['userId'] = user_id
        
        logger.info(f"Note created: {title}")
        return note_doc
    
    @staticmethod
    def get_by_user(db, user_id: str, skip: int = 0, limit: int = 50,
                    search: str = None, topic: str = None, subject: str = None) -> list:
        """Get user's notes with optional filters"""
        query = {'userId': ObjectId(user_id)}
        
        if search:
            query['$text'] = {'$search': search}
        
        if topic:
            query['topic'] = topic
        elif subject:
            query['subject'] = subject
        
        notes = list(db.notes.find(query)
                     .sort('createdAt', -1)
                     .skip(skip)
                     .limit(limit))
        
        for note in notes:
            note['_id'] = str(note['_id'])
            note['userId'] = user_id
        
        return notes
    
    @staticmethod
    def get_by_id(db, note_id: str, user_id: str = None) -> dict:
        """Get note by ID"""
        try:
            query = {'_id': ObjectId(note_id)}
            if user_id:
                query['userId'] = ObjectId(user_id)
            
            note = db.notes.find_one(query)
            if note:
                note['_id'] = str(note['_id'])
                note['userId'] = str(note['userId'])
            return note
        except Exception as e:
            logger.error(f"Error finding note: {str(e)}")
            return None
    
    @staticmethod
    def update(db, note_id: str, user_id: str, **kwargs) -> dict:
        """Update note (only title allowed)"""
        try:
            allowed_fields = {'title'}
            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not update_data:
                raise ValueError("No valid fields to update")
            
            update_data['updatedAt'] = datetime.utcnow()
            
            note = db.notes.find_one_and_update(
                {'_id': ObjectId(note_id), 'userId': ObjectId(user_id)},
                {'$set': update_data},
                return_document=True
            )
            
            if note:
                note['_id'] = str(note['_id'])
                note['userId'] = user_id
            
            return note
        except Exception as e:
            logger.error(f"Error updating note: {str(e)}")
            return None
    
    @staticmethod
    def delete(db, note_id: str, user_id: str) -> bool:
        """Delete note and associated flashcards"""
        try:
            note_oid = ObjectId(note_id)
            user_oid = ObjectId(user_id)
            
            # Delete associated flashcards
            db.flashcards.delete_many({
                'noteId': note_oid,
                'userId': user_oid
            })
            
            # Delete note
            result = db.notes.delete_one({
                '_id': note_oid,
                'userId': user_oid
            })
            
            logger.info(f"Note deleted: {note_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting note: {str(e)}")
            return False
    
    @staticmethod
    def get_all_subjects(db, user_id: str) -> list:
        """Get all unique subjects for user"""
        try:
            subjects = db.notes.distinct('subject', {'userId': ObjectId(user_id)})
            return subjects
        except Exception as e:
            logger.error(f"Error getting subjects: {str(e)}")
            return []
    
    @staticmethod
    def get_all_topics(db, user_id: str) -> list:
        """Get all unique topics for user"""
        try:
            pipeline = [
                {'$match': {'userId': ObjectId(user_id)}},
                {'$unwind': '$topics'},
                {'$group': {'_id': '$topics'}},
                {'$sort': {'_id': 1}}
            ]
            topics = [doc['_id'] for doc in db.notes.aggregate(pipeline)]
            return topics
        except Exception as e:
            logger.error(f"Error getting topics: {str(e)}")
            return []
