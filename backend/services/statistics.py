"""Statistics and reporting services"""

from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for generating user statistics"""
    
    @staticmethod
    def get_dashboard_stats(db, user_id: str) -> dict:
        """Get comprehensive dashboard statistics"""
        try:
            user_oid = ObjectId(user_id)
            
            # Flashcard statistics
            total_cards = db.flashcards.count_documents({'userId': user_oid})
            known_cards = db.flashcards.count_documents({'userId': user_oid, 'known': True})
            revision_cards = db.flashcards.count_documents({'userId': user_oid, 'revisionPriority': {'$in': ['high', 'medium']}})
            favorite_cards = db.flashcards.count_documents({'userId': user_oid, 'favorite': True})
            
            # Note statistics
            total_notes = db.notes.count_documents({'userId': user_oid})
            
            # Completion percentage
            completion = round((known_cards / total_cards * 100) if total_cards > 0 else 0, 2)
            
            # Average confidence
            avg_pipeline = [
                {'$match': {'userId': user_oid}},
                {'$group': {'_id': None, 'avgConfidence': {'$avg': '$confidence'}}}
            ]
            avg_result = list(db.flashcards.aggregate(avg_pipeline))
            avg_confidence = round(avg_result[0]['avgConfidence'], 2) if avg_result else 0
            
            # Average difficulty
            difficulty_pipeline = [
                {'$match': {'userId': user_oid}},
                {
                    '$group': {
                        '_id': '$difficulty',
                        'count': {'$sum': 1}
                    }
                }
            ]
            difficulty_dist = {}
            for doc in db.flashcards.aggregate(difficulty_pipeline):
                difficulty_dist[doc['_id']] = doc['count']
            
            avg_difficulty = "Medium"  # Default
            if difficulty_dist:
                max_diff = max(difficulty_dist.values())
                for diff, count in difficulty_dist.items():
                    if count == max_diff:
                        avg_difficulty = diff
                        break
            
            # Subject distribution
            subject_pipeline = [
                {'$match': {'userId': user_oid}},
                {'$group': {'_id': '$subject', 'count': {'$sum': 1}}}
            ]
            subject_dist = {doc['_id']: doc['count'] for doc in db.notes.aggregate(subject_pipeline)}
            
            # Weekly activity
            week_ago = datetime.utcnow() - timedelta(days=7)
            weekly_activity = db.flashcards.count_documents({
                'userId': user_oid,
                'lastReviewedAt': {'$gte': week_ago}
            })
            
            # Streak calculation
            streak = StatisticsService._calculate_streak(db, user_id)
            
            return {
                'cards': {
                    'total': total_cards,
                    'known': known_cards,
                    'notKnown': total_cards - known_cards,
                    'revision': revision_cards,
                    'favorite': favorite_cards
                },
                'notes': {
                    'total': total_notes
                },
                'completion': completion,
                'avgConfidence': avg_confidence,
                'avgDifficulty': avg_difficulty,
                'subjectDistribution': subject_dist,
                'difficultyDistribution': difficulty_dist,
                'weeklyActivity': weekly_activity,
                'streak': streak
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_streak(db, user_id: str) -> int:
        """Calculate user's learning streak"""
        try:
            user_oid = ObjectId(user_id)
            
            # Get all review dates
            pipeline = [
                {'$match': {'userId': user_oid, 'lastReviewedAt': {'$ne': None}}},
                {'$group': {
                    '_id': {
                        'year': {'$year': '$lastReviewedAt'},
                        'month': {'$month': '$lastReviewedAt'},
                        'day': {'$dayOfMonth': '$lastReviewedAt'}
                    }
                }},
                {'$sort': {'_id': -1}}
            ]
            
            review_dates = list(db.flashcards.aggregate(pipeline))
            
            if not review_dates:
                return 0
            
            streak = 1
            for i in range(len(review_dates) - 1):
                current_date = f"{review_dates[i]['_id']['year']}-{review_dates[i]['_id']['month']:02d}-{review_dates[i]['_id']['day']:02d}"
                next_date = f"{review_dates[i+1]['_id']['year']}-{review_dates[i+1]['_id']['month']:02d}-{review_dates[i+1]['_id']['day']:02d}"
                
                current = datetime.strptime(current_date, '%Y-%m-%d')
                next_dt = datetime.strptime(next_date, '%Y-%m-%d')
                
                # Check if dates are consecutive
                if (current - next_dt).days == 1:
                    streak += 1
                else:
                    break
            
            return streak
        except Exception as e:
            logger.error(f"Error calculating streak: {str(e)}")
            return 0
    
    @staticmethod
    def get_subject_stats(db, user_id: str, subject: str) -> dict:
        """Get statistics for a specific subject"""
        try:
            user_oid = ObjectId(user_id)
            
            notes = list(db.notes.find({'userId': user_oid, 'subject': subject}))
            note_ids = [note['_id'] for note in notes]
            
            if not note_ids:
                return {}
            
            cards = list(db.flashcards.find({'userId': user_oid, 'noteId': {'$in': note_ids}}))
            
            return {
                'subject': subject,
                'notes': len(notes),
                'cards': len(cards),
                'known': sum(1 for c in cards if c['known']),
                'favorite': sum(1 for c in cards if c['favorite']),
                'avgConfidence': round(sum(c['confidence'] for c in cards) / len(cards), 2) if cards else 0
            }
        except Exception as e:
            logger.error(f"Error getting subject stats: {str(e)}")
            return {}
