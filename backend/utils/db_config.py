from pymongo import MongoClient, ASCENDING, DESCENDING
from flask import current_app, g
import os
from datetime import datetime
import logging

def init_db(app):
    """Initialize database connection and create indexes"""
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/medicine_db')
    
    # Test connection on startup
    try:
        mongo_uri = app.config['MONGO_URI']
        client = MongoClient(mongo_uri)
        
        # Handle different URI formats
        if 'mongodb+srv://' in mongo_uri or mongo_uri.count('/') < 3:
            # MongoDB Atlas or URI without database name
            db_name = 'medicine_db'
        else:
            # Local MongoDB URI with database name
            db_path = mongo_uri.split('/')[-1]
            db_name = db_path.split('?')[0] if '?' in db_path else db_path
            if not db_name:  # Empty string
                db_name = 'medicine_db'
        
        db = client[db_name]  # Use bracket notation
        # Test connection
        db.command('ping')
        print(f"✓ MongoDB connection successful (database: {db_name})")
        
        # Create indexes
        create_indexes(db)
        
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("Note: MongoDB is optional for ML functionality")

def get_db():
    """Get database connection"""
    if 'db' not in g:
        try:
            mongo_uri = current_app.config['MONGO_URI']
            client = MongoClient(mongo_uri)
            
            # Handle different URI formats
            if 'mongodb+srv://' in mongo_uri or mongo_uri.count('/') < 3:
                # MongoDB Atlas or URI without database name
                db_name = 'medicine_db'
            else:
                # Local MongoDB URI with database name
                db_path = mongo_uri.split('/')[-1]
                db_name = db_path.split('?')[0] if '?' in db_path else db_path
                if not db_name:  # Empty string
                    db_name = 'medicine_db'
            
            g.db = client[db_name]
            
            # Test the connection
            g.db.command('ping')
            
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            g.db = None
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.client.close()

def create_indexes(db):
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.users.create_index([("created_at", DESCENDING)])
        
        # Prescriptions collection indexes
        db.prescriptions.create_index([("patient_id", ASCENDING)])
        db.prescriptions.create_index([("created_at", DESCENDING)])
        db.prescriptions.create_index([("predicted_disease", ASCENDING)])
        
        # Prediction logs collection indexes
        db.prediction_logs.create_index([("timestamp", DESCENDING)])
        db.prediction_logs.create_index([("user_id", ASCENDING)])
        
        print("✓ Database indexes created successfully")
    except Exception as e:
        print(f"✗ Failed to create indexes: {e}")

def save_prediction_log(user_id, symptoms, prediction_result, metadata=None):
    """Save prediction to database for analytics"""
    db = get_db()
    if db is None:
        return None
    
    try:
        log_entry = {
            'user_id': user_id,
            'symptoms': symptoms,
            'predicted_disease': prediction_result.get('predicted_disease'),
            'confidence': prediction_result.get('confidence'),
            'success': prediction_result.get('success'),
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        
        result = db.prediction_logs.insert_one(log_entry)
        return str(result.inserted_id)
        
    except Exception as e:
        logging.error(f"Failed to save prediction log: {e}")
        return None

def get_user_prediction_history(user_id, limit=10):
    """Get user's prediction history"""
    db = get_db()
    if db is None:
        return []
    
    try:
        cursor = db.prediction_logs.find(
            {'user_id': user_id}
        ).sort('timestamp', DESCENDING).limit(limit)
        
        return list(cursor)
        
    except Exception as e:
        logging.error(f"Failed to get prediction history: {e}")
        return []

def get_system_stats():
    """Get system statistics for admin dashboard"""
    db = get_db()
    if db is None:
        return {}
    
    try:
        stats = {}
        
        # Total users
        stats['total_users'] = db.users.count_documents({})
        
        # Total predictions
        stats['total_predictions'] = db.prediction_logs.count_documents({})
        
        # Predictions today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        stats['predictions_today'] = db.prediction_logs.count_documents({
            'timestamp': {'$gte': today}
        })
        
        # Most common diseases
        pipeline = [
            {'$match': {'success': True}},
            {'$group': {'_id': '$predicted_disease', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        stats['common_diseases'] = list(db.prediction_logs.aggregate(pipeline))
        
        # Active users (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        stats['active_users'] = db.users.count_documents({
            'last_login': {'$gte': week_ago}
        })
        
        return stats
        
    except Exception as e:
        logging.error(f"Failed to get system stats: {e}")
        return {}

# User management functions
def create_user(user_data):
    """Create a new user"""
    db = get_db()
    if db is None:
        logging.error("create_user: Database connection is None")
        return None
    
    try:
        user_data['created_at'] = datetime.utcnow()
        user_data['last_login'] = None
        user_data['is_active'] = True
        
        logging.info(f"create_user: Attempting to insert user with email {user_data.get('email')}")
        result = db.users.insert_one(user_data)
        logging.info(f"create_user: User created with ID {result.inserted_id}")
        return str(result.inserted_id)
        
    except Exception as e:
        logging.error(f"Failed to create user: {e}")
        logging.error(f"User data: {user_data}")
        return None

def get_user_by_email(email):
    """Get user by email"""
    db = get_db()
    if db is None:
        return None
    
    try:
        return db.users.find_one({'email': email})
    except Exception as e:
        logging.error(f"Failed to get user by email: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    db = get_db()
    if db is None:
        return None
    
    try:
        from bson import ObjectId
        return db.users.find_one({'_id': ObjectId(user_id)})
    except Exception as e:
        logging.error(f"Failed to get user by ID: {e}")
        return None

def update_user_login(user_id):
    """Update user's last login time"""
    db = get_db()
    if db is None:
        return False
    
    try:
        from bson import ObjectId
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        return result.modified_count > 0
        
    except Exception as e:
        logging.error(f"Failed to update user login: {e}")
        return False
