from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db_config import create_user, get_user_by_email, get_user_by_id, update_user_login, get_db
from datetime import datetime, timedelta
from bson import ObjectId
import re
import secrets
import hashlib

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Extract and validate required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', 'patient').lower()
        
        # Validation
        if not all([email, password, first_name, last_name]):
            return jsonify({
                'success': False,
                'message': 'Email, password, first name, and last name are required'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        if role not in ['patient', 'doctor', 'admin']:
            role = 'patient'  # Default to patient
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 409
        
        # Create user data
        user_data = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'profile': {
                'age': data.get('age'),
                'gender': data.get('gender'),
                'phone': data.get('phone', '').strip()
            }
        }
        
        # Create user
        user_id = create_user(user_data)
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Failed to create user account'
            }), 500
        
        # Create access token
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role
            },
            'access_token': access_token
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Get user from database
        user = get_user_by_email(email)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Check if account is active
        if not user.get('is_active', True):
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 401
        
        # Verify password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Update last login
        user_id = str(user['_id'])
        update_user_login(user_id)
        
        # Create access token
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user_id,
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role']
            },
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Remove sensitive information
        user_data = {
            'id': str(user['_id']),
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role'],
            'profile': user.get('profile', {}),
            'created_at': user.get('created_at'),
            'last_login': user.get('last_login')
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get profile',
            'error': str(e)
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Get current user
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name']
        allowed_profile_fields = ['age', 'gender', 'phone']
        
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]
        
        # Update profile fields
        if 'profile' in data and isinstance(data['profile'], dict):
            profile_updates = {}
            for field in allowed_profile_fields:
                if field in data['profile']:
                    profile_updates[f'profile.{field}'] = data['profile'][field]
            update_data.update(profile_updates)
        
        if not update_data:
            return jsonify({
                'success': False,
                'message': 'No valid fields to update'
            }), 400
        
        # Update user in database
        from utils.db_config import get_db
        from bson import ObjectId
        
        db = get_db()
        if db:
            result = db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                # Get updated user
                updated_user = get_user_by_id(user_id)
                user_data = {
                    'id': str(updated_user['_id']),
                    'email': updated_user['email'],
                    'first_name': updated_user['first_name'],
                    'last_name': updated_user['last_name'],
                    'role': updated_user['role'],
                    'profile': updated_user.get('profile', {})
                }
                
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'user': user_data
                }), 200
        
        return jsonify({
            'success': False,
            'message': 'Failed to update profile'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Profile update failed',
            'error': str(e)
        }), 500

@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    """Validate JWT token"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401
        
        return jsonify({
            'success': True,
            'message': 'Token is valid',
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Token validation failed',
            'error': str(e)
        }), 401

# Demo login for testing without database
@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    """Demo login that doesn't require database"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Demo credentials
        if email == 'demo@medicine.com' and password == 'demo123':
            # Create demo access token
            access_token = create_access_token(
                identity='demo_user_123',
                expires_delta=timedelta(days=1)
            )
            
            return jsonify({
                'success': True,
                'message': 'Demo login successful',
                'user': {
                    'id': 'demo_user_123',
                    'email': 'demo@medicine.com',
                    'first_name': 'Demo',
                    'last_name': 'User',
                    'role': 'patient'
                },
                'access_token': access_token
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Invalid demo credentials. Use demo@medicine.com / demo123'
        }), 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Demo login failed',
            'error': str(e)
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Generate password reset token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Check if user exists
        user = get_user_by_email(email)
        if not user:
            # Don't reveal if user exists or not for security
            return jsonify({
                'success': True,
                'message': 'If an account exists with this email, you will receive reset instructions'
            }), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Store reset token in database (expires in 1 hour)
        db = get_db()
        if db:
            db.users.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'reset_token': token_hash,
                        'reset_token_expires': datetime.utcnow() + timedelta(hours=1)
                    }
                }
            )
        
        # In a real app, you would send an email here
        # For demo purposes, we'll return the token (NEVER do this in production!)
        return jsonify({
            'success': True,
            'message': 'Password reset instructions sent to your email',
            'reset_token': reset_token  # Only for development/demo purposes
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to process password reset request',
            'error': str(e)
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        reset_token = data.get('token', '')
        new_password = data.get('password', '')
        
        if not reset_token or not new_password:
            return jsonify({
                'success': False,
                'message': 'Token and new password are required'
            }), 400
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Hash the token to compare with stored hash
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Find user with matching token that hasn't expired
        db = get_db()
        if db:
            user = db.users.find_one({
                'reset_token': token_hash,
                'reset_token_expires': {'$gt': datetime.utcnow()}
            })
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired reset token'
                }), 400
            
            # Update password and remove reset token
            result = db.users.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'password_hash': generate_password_hash(new_password)
                    },
                    '$unset': {
                        'reset_token': '',
                        'reset_token_expires': ''
                    }
                }
            )
            
            if result.modified_count > 0:
                return jsonify({
                    'success': True,
                    'message': 'Password reset successfully'
                }), 200
        
        return jsonify({
            'success': False,
            'message': 'Failed to reset password'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Password reset failed',
            'error': str(e)
        }), 500
