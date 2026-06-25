"""Database utility functions and initialization"""

import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from config import Config
import logging

logger = logging.getLogger(__name__)

# Global database instance
db = None
client = None


def init_db(app=None):
    """Initialize MongoDB connection"""
    global db, client
    
    try:
        if app:
            mongodb_uri = app.config.get('MONGODB_URI')
            mongodb_db_name = app.config.get('MONGODB_DB_NAME')
        else:
            config = Config()
            mongodb_uri = getattr(config, 'MONGODB_URI', None)
            mongodb_db_name = getattr(config, 'MONGODB_DB_NAME', 'smartflashcard')
        
        # Fallback to defaults if not set
        if not mongodb_uri:
            mongodb_uri = 'mongodb://localhost:27017/smartflashcard'
        if not mongodb_db_name:
            mongodb_db_name = 'smartflashcard'
        
        client_kwargs = {
            'serverSelectionTimeoutMS': 5000,
            'connectTimeoutMS': 10000,
        }

        if mongodb_uri.startswith('mongodb+srv://') or 'mongodb.net' in mongodb_uri:
            client_kwargs['tls'] = True
            client_kwargs['tlsCAFile'] = certifi.where()

        logger.info('MongoDB URI: %s', mongodb_uri)
        logger.info('MongoDB client kwargs: %s', {k: v for k, v in client_kwargs.items() if k != 'tlsCAFile'})

        client = MongoClient(
            mongodb_uri,
            **client_kwargs,
        )
        
        # Test connection
        client.admin.command('ping')
        db = client[mongodb_db_name]
        
        # Create indexes
        create_indexes(db)
        
        logger.info(f"Connected to MongoDB: {mongodb_db_name}")
        return db
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


def get_db():
    """Get database instance"""
    global db
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db


def close_db():
    """Close database connection"""
    global client, db
    if client:
        client.close()
        db = None
        client = None
        logger.info("Database connection closed")


def create_indexes(db):
    """Create necessary indexes for collections"""
    
    def safe_create_index(collection, *keys, **kwargs):
        try:
            collection.create_index(*keys, **kwargs)
        except OperationFailure as e:
            if e.code == 85 and 'equivalent index already exists' in str(e):
                logger.warning('Equivalent index already exists on %s; skipping: %s %s', collection.name, keys, kwargs)
                return
            raise
    
    # Users collection indexes
    safe_create_index(db.users, "email", unique=True)
    safe_create_index(db.users, "createdAt")
    
    # Notes collection indexes
    safe_create_index(db.notes, "userId")
    safe_create_index(db.notes, "subject")
    safe_create_index(db.notes, "topic")
    safe_create_index(db.notes, "createdAt")
    safe_create_index(db.notes, [("title", "text"), ("subject", "text"), ("topic", "text"), ("topics", "text")])
    
    # Flashcards collection indexes
    safe_create_index(db.flashcards, "userId")
    safe_create_index(db.flashcards, "noteId")
    safe_create_index(db.flashcards, "difficulty")
    safe_create_index(db.flashcards, "known")
    safe_create_index(db.flashcards, "favorite")
    safe_create_index(db.flashcards, "createdAt")
    safe_create_index(db.flashcards, [("question", "text"), ("answer", "text"), ("topic", "text")])
    
    # Favorites collection indexes
    safe_create_index(db.favorites, "userId")
    safe_create_index(db.favorites, "flashcardId")
    safe_create_index(db.favorites, "createdAt")
    
    # Revision collection indexes
    safe_create_index(db.revision, "userId")
    safe_create_index(db.revision, "flashcardId")
    safe_create_index(db.revision, "priority")
    safe_create_index(db.revision, "createdAt")
    
    # History collection indexes
    safe_create_index(db.history, "userId")
    safe_create_index(db.history, "subject")
    safe_create_index(db.history, "topic")
    safe_create_index(db.history, "createdAt")
    safe_create_index(db.history, [("title", "text"), ("subject", "text"), ("topic", "text")])
    
    # Statistics collection indexes
    safe_create_index(db.statistics, "userId", unique=True)
    safe_create_index(db.statistics, "updatedAt")
    
    logger.info("Database indexes created successfully")
