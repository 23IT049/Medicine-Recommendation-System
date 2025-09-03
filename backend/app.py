from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.admin import admin_bp
from routes.ml import ml_bp
from utils.db_config import init_db, close_db
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS configuration to prevent timeout issues
CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/medicine_db')
# Set JWT token to expire in 24 hours instead of never expiring
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
# Prevent timeout issues
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# JWT Manager
jwt = JWTManager(app)

# Initialize Database
init_db(app)

# Register database teardown
app.teardown_appcontext(close_db)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(ml_bp, url_prefix='/api/ml')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "Medicine Prediction System API is running",
        "version": "1.0.0"
    }), 200

@app.route('/api/db-test', methods=['GET'])
def db_test():
    """Test database connection"""
    try:
        from utils.db_config import get_db
        from pymongo import MongoClient
        import os
        
        # Test direct connection first
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/medicine_db')
        
        try:
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
            
            db_direct = client[db_name]
            db_direct.command('ping')
            direct_status = "success"
            direct_error = None
        except Exception as e:
            direct_status = "failed"
            direct_error = str(e)
            db_name = 'unknown'
        
        # Test Flask g connection
        try:
            db = get_db()
            if db is None:
                flask_status = "failed - db is None"
                flask_error = "get_db() returned None"
            else:
                db.command('ping')
                user_count = db.users.count_documents({})
                flask_status = "success"
                flask_error = None
        except Exception as e:
            flask_status = "failed"
            flask_error = str(e)
            user_count = 0
        
        return jsonify({
            "status": "info",
            "mongo_uri": mongo_uri,
            "db_name": db_name,
            "direct_connection": {
                "status": direct_status,
                "error": direct_error
            },
            "flask_connection": {
                "status": flask_status,
                "error": flask_error,
                "user_count": user_count if flask_status == "success" else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database test failed: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
