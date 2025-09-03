#!/usr/bin/env python
"""
Improved server script with better configuration and error handling
"""

from flask import Flask
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
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Enhanced CORS configuration to prevent timeout issues
    CORS(app, 
         origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Credentials'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         max_age=86400  # Cache preflight requests for 24 hours
    )
    
    # Enhanced configuration
    app.config.update(
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production'),
        MONGO_URI=os.getenv('MONGO_URI', 'mongodb://localhost:27017/medicine_db'),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24),  # 24 hour token expiry
        SEND_FILE_MAX_AGE_DEFAULT=0,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        JSON_SORT_KEYS=False,  # Don't sort JSON keys
        JSONIFY_PRETTYPRINT_REGULAR=True  # Pretty print JSON in development
    )
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired', 'success': False}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Invalid token', 'success': False}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'message': 'Authorization token required', 'success': False}, 401
    
    # Initialize Database
    try:
        init_db(app)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Register database teardown
    app.teardown_appcontext(close_db)
    
    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')  
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    
    # Health check endpoints
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from utils.db_config import get_db
        
        try:
            # Test database connection
            db = get_db()
            db_status = "connected" if db is not None else "disconnected"
            
            return {
                "status": "healthy",
                "message": "Medicine Prediction System API is running",
                "version": "1.0.0",
                "database": db_status,
                "environment": os.getenv('FLASK_ENV', 'development')
            }, 200
        except Exception as e:
            return {
                "status": "unhealthy", 
                "message": f"Health check failed: {str(e)}"
            }, 500
    
    @app.route('/api/status', methods=['GET'])
    def status_check():
        """Detailed status endpoint"""
        from utils.db_config import get_db
        
        try:
            db = get_db()
            user_count = db.users.count_documents({}) if db else 0
            prediction_count = db.prediction_logs.count_documents({}) if db else 0
            
            return {
                "status": "operational",
                "database": {
                    "connected": db is not None,
                    "users": user_count,
                    "predictions": prediction_count
                },
                "services": {
                    "auth": "operational",
                    "ml": "operational", 
                    "patient": "operational",
                    "admin": "operational"
                }
            }, 200
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {"status": "degraded", "error": str(e)}, 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found', 'success': False}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error', 'success': False}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'success': False}, 400
    
    return app

def main():
    """Main entry point"""
    app = create_app()
    
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        # Run the server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,  # Enable threading for better performance
            use_reloader=debug  # Only use reloader in development
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise

if __name__ == '__main__':
    main()
