"""User model and database operations"""

from datetime import datetime
from bson import ObjectId
import bcrypt
import logging

logger = logging.getLogger(__name__)


class User:
    """User model"""
    
    @staticmethod
    def create(db, email: str, password: str, name: str) -> dict:
        """
        Create new user
        
        Args:
            db: MongoDB database instance
            email: User email
            password: Plain text password
            name: Full name
        
        Returns:
            User document
        """
        # Check if user exists
        if db.users.find_one({'email': email}):
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_doc = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = db.users.insert_one(user_doc)
        user_doc['_id'] = str(result.inserted_id)
        
        logger.info(f"User created: {email}")
        return user_doc
    
    @staticmethod
    def find_by_id(db, user_id: str) -> dict:
        """Find user by ID"""
        try:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            logger.error(f"Error finding user: {str(e)}")
            return None
    
    @staticmethod
    def find_by_email(db, email: str) -> dict:
        """Find user by email"""
        user = db.users.find_one({'email': email})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def _normalize_password_hash(password_hash):
        """Return the stored hash as bytes for bcrypt verification."""
        if isinstance(password_hash, bytes):
            return password_hash
        if isinstance(password_hash, str):
            return password_hash.encode('utf-8')
        raise ValueError("Invalid stored password format")

    @staticmethod
    def verify_password(db, email: str, password: str) -> bool:
        """
        Verify user password
        
        Args:
            db: MongoDB database instance
            email: User email
            password: Plain text password
        
        Returns:
            True if password is correct, False otherwise
        """
        user = db.users.find_one({'email': email})
        if not user:
            return False

        stored_password = user.get('password')
        if stored_password is None:
            return False

        try:
            stored_password = User._normalize_password_hash(stored_password)
        except ValueError:
            return False

        return bcrypt.checkpw(
            password.encode('utf-8'),
            stored_password
        )
    
    @staticmethod
    def update_profile(db, user_id: str, **kwargs) -> dict:
        """
        Update user profile (only name is allowed)
        
        Args:
            db: MongoDB database instance
            user_id: User ID
            **kwargs: Fields to update (only 'name' is allowed)
        
        Returns:
            Updated user document
        """
        # Only allow name to be updated
        allowed_fields = {'name'}
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            raise ValueError("No valid fields to update")
        
        update_data['updatedAt'] = datetime.utcnow()
        
        result = db.users.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': update_data},
            return_document=True
        )
        
        if result:
            result['_id'] = str(result['_id'])
            logger.info(f"User profile updated: {user_id}")
        
        return result
    
    @staticmethod
    def change_password(db, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            db: MongoDB database instance
            user_id: User ID
            old_password: Current password
            new_password: New password
        
        Returns:
            True if password changed successfully
        """
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        try:
            stored_password = User._normalize_password_hash(user['password'])
        except ValueError:
            raise ValueError("Invalid stored password format")

        if not bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
            raise ValueError("Old password is incorrect")
        
        # Hash new password
        hashed_password = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'password': hashed_password,
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Password changed for user: {user_id}")
        return True
