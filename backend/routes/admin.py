from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db_config import get_db, get_user_by_id, get_system_stats
from datetime import datetime, timedelta
from bson import ObjectId
import logging

admin_bp = Blueprint('admin', __name__)

def check_admin_access(user_id):
    """Check if user has admin access"""
    user = get_user_by_id(user_id)
    if not user:
        return False, 'User not found'
    
    if user.get('role') != 'admin':
        return False, 'Access denied: Admin privileges required'
    
    return True, None

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    """Get comprehensive admin dashboard data"""
    try:
        user_id = get_jwt_identity()
        
        # Check admin access
        has_access, error_msg = check_admin_access(user_id)
        if not has_access:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 403
        
        db = get_db()
        if db is None:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500
        
        # Get system statistics
        stats = get_system_stats()
        
        # Get recent user registrations
        recent_users = list(db.users.find(
            {}, 
            {'first_name': 1, 'last_name': 1, 'email': 1, 'role': 1, 'created_at': 1, 'last_login': 1}
        ).sort('created_at', -1).limit(10))
        
        # Format recent users
        formatted_users = []
        for user in recent_users:
            user['_id'] = str(user['_id'])
            if 'created_at' in user and user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
            if 'last_login' in user and user['last_login']:
                user['last_login'] = user['last_login'].isoformat()
            formatted_users.append(user)
        
        # Get recent predictions (system-wide)
        recent_predictions = list(db.prediction_logs.find(
            {},
            {'user_id': 1, 'predicted_disease': 1, 'confidence': 1, 'timestamp': 1, 'success': 1}
        ).sort('timestamp', -1).limit(15))
        
        # Format predictions
        formatted_predictions = []
        for pred in recent_predictions:
            pred['_id'] = str(pred['_id'])
            if 'timestamp' in pred and pred['timestamp']:
                pred['timestamp'] = pred['timestamp'].isoformat()
            formatted_predictions.append(pred)
        
        # Calculate additional metrics
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Users registered this week/month
        users_this_week = db.users.count_documents({'created_at': {'$gte': week_ago}})
        users_this_month = db.users.count_documents({'created_at': {'$gte': month_ago}})
        
        # Predictions this week/month
        predictions_this_week = db.prediction_logs.count_documents({'timestamp': {'$gte': week_ago}})
        predictions_this_month = db.prediction_logs.count_documents({'timestamp': {'$gte': month_ago}})
        
        # User role distribution
        role_stats = list(db.users.aggregate([
            {'$group': {'_id': '$role', 'count': {'$sum': 1}}}
        ]))
        
        # Success rate (predictions with success=True)
        total_predictions = db.prediction_logs.count_documents({})
        successful_predictions = db.prediction_logs.count_documents({'success': True})
        success_rate = (successful_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        # Weekly prediction trend (last 4 weeks)
        weekly_trend = []
        for i in range(4):
            week_start = now - timedelta(weeks=i+1)
            week_end = now - timedelta(weeks=i)
            count = db.prediction_logs.count_documents({
                'timestamp': {'$gte': week_start, '$lt': week_end}
            })
            weekly_trend.append({
                'week': f'Week {4-i}',
                'count': count,
                'start_date': week_start.isoformat(),
                'end_date': week_end.isoformat()
            })
        
        return jsonify({
            'success': True,
            'system_stats': {
                'total_users': stats.get('total_users', 0),
                'total_predictions': stats.get('total_predictions', 0),
                'predictions_today': stats.get('predictions_today', 0),
                'active_users': stats.get('active_users', 0),
                'users_this_week': users_this_week,
                'users_this_month': users_this_month,
                'predictions_this_week': predictions_this_week,
                'predictions_this_month': predictions_this_month,
                'success_rate': round(success_rate, 2)
            },
            'role_distribution': role_stats,
            'common_diseases': stats.get('common_diseases', []),
            'recent_users': formatted_users,
            'recent_predictions': formatted_predictions,
            'weekly_trend': weekly_trend
        })
        
    except Exception as e:
        logging.error(f"Admin dashboard error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to fetch admin dashboard data: {str(e)}'
        }), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users with pagination and filtering"""
    try:
        user_id = get_jwt_identity()
        
        # Check admin access
        has_access, error_msg = check_admin_access(user_id)
        if not has_access:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 403
        
        db = get_db()
        if db is None:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        role_filter = request.args.get('role')
        search = request.args.get('search', '').strip()
        
        # Build query
        query = {}
        if role_filter and role_filter != 'all':
            query['role'] = role_filter
        
        if search:
            query['$or'] = [
                {'first_name': {'$regex': search, '$options': 'i'}},
                {'last_name': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}}
            ]
        
        # Get total count
        total_count = db.users.count_documents(query)
        
        # Get users with pagination
        skip = (page - 1) * limit
        users = list(db.users.find(
            query,
            {'password_hash': 0}  # Exclude password hash
        ).sort('created_at', -1).skip(skip).limit(limit))
        
        # Format users
        formatted_users = []
        for user in users:
            user['_id'] = str(user['_id'])
            if 'created_at' in user and user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
            if 'last_login' in user and user['last_login']:
                user['last_login'] = user['last_login'].isoformat()
            formatted_users.append(user)
        
        return jsonify({
            'success': True,
            'users': formatted_users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })
        
    except Exception as e:
        logging.error(f"Admin get users error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to fetch users: {str(e)}'
        }), 500

@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    try:
        admin_user_id = get_jwt_identity()
        
        # Check admin access
        has_access, error_msg = check_admin_access(admin_user_id)
        if not has_access:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 403
        
        db = get_db()
        if db is None:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500
        
        # Get user
        user = db.users.find_one(
            {'_id': ObjectId(user_id)},
            {'password_hash': 0}  # Exclude password hash
        )
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get user's prediction history
        predictions = list(db.prediction_logs.find(
            {'user_id': user_id}
        ).sort('timestamp', -1).limit(20))
        
        # Format data
        user['_id'] = str(user['_id'])
        if 'created_at' in user and user['created_at']:
            user['created_at'] = user['created_at'].isoformat()
        if 'last_login' in user and user['last_login']:
            user['last_login'] = user['last_login'].isoformat()
        
        formatted_predictions = []
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            if 'timestamp' in pred and pred['timestamp']:
                pred['timestamp'] = pred['timestamp'].isoformat()
            formatted_predictions.append(pred)
        
        # Calculate user stats
        total_predictions = len(predictions)
        successful_predictions = len([p for p in predictions if p.get('success')])
        success_rate = (successful_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        return jsonify({
            'success': True,
            'user': user,
            'predictions': formatted_predictions,
            'stats': {
                'total_predictions': total_predictions,
                'successful_predictions': successful_predictions,
                'success_rate': round(success_rate, 2)
            }
        })
        
    except Exception as e:
        logging.error(f"Admin get user details error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to fetch user details: {str(e)}'
        }), 500

@admin_bp.route('/users/<user_id>/toggle-status', methods=['PUT'])
@jwt_required()
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    try:
        admin_user_id = get_jwt_identity()
        
        # Check admin access
        has_access, error_msg = check_admin_access(admin_user_id)
        if not has_access:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 403
        
        # Prevent admin from disabling themselves
        if user_id == admin_user_id:
            return jsonify({
                'success': False,
                'message': 'Cannot modify your own account status'
            }), 400
        
        db = get_db()
        if db is None:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500
        
        # Get current status
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Toggle status
        new_status = not user.get('is_active', True)
        
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': new_status}}
        )
        
        if result.modified_count > 0:
            status_text = 'activated' if new_status else 'deactivated'
            return jsonify({
                'success': True,
                'message': f'User {status_text} successfully',
                'is_active': new_status
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update user status'
            }), 500
        
    except Exception as e:
        logging.error(f"Admin toggle user status error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to toggle user status: {str(e)}'
        }), 500

@admin_bp.route('/analytics/predictions', methods=['GET'])
@jwt_required()
def get_prediction_analytics():
    """Get detailed prediction analytics"""
    try:
        user_id = get_jwt_identity()
        
        # Check admin access
        has_access, error_msg = check_admin_access(user_id)
        if not has_access:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 403
        
        db = get_db()
        if db is None:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500
        
        # Get time range from query parameters
        days = int(request.args.get('days', 30))  # Default last 30 days
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily prediction counts
        daily_pipeline = [
            {'$match': {'timestamp': {'$gte': start_date}}},
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$timestamp'},
                        'month': {'$month': '$timestamp'},
                        'day': {'$dayOfMonth': '$timestamp'}
                    },
                    'count': {'$sum': 1},
                    'successful': {
                        '$sum': {
                            '$cond': [{'$eq': ['$success', True]}, 1, 0]
                        }
                    }
                }
            },
            {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}}
        ]
        
        daily_stats = list(db.prediction_logs.aggregate(daily_pipeline))
        
        # Disease frequency
        disease_pipeline = [
            {'$match': {'timestamp': {'$gte': start_date}, 'success': True}},
            {
                '$group': {
                    '_id': '$predicted_disease',
                    'count': {'$sum': 1},
                    'avg_confidence': {'$avg': '$confidence'}
                }
            },
            {'$sort': {'count': -1}},
            {'$limit': 15}
        ]
        
        disease_stats = list(db.prediction_logs.aggregate(disease_pipeline))
        
        # Average confidence by disease
        confidence_pipeline = [
            {'$match': {'timestamp': {'$gte': start_date}, 'success': True}},
            {
                '$group': {
                    '_id': '$predicted_disease',
                    'avg_confidence': {'$avg': '$confidence'},
                    'min_confidence': {'$min': '$confidence'},
                    'max_confidence': {'$max': '$confidence'},
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'avg_confidence': -1}}
        ]
        
        confidence_stats = list(db.prediction_logs.aggregate(confidence_pipeline))
        
        return jsonify({
            'success': True,
            'time_range': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat()
            },
            'daily_predictions': daily_stats,
            'disease_frequency': disease_stats,
            'confidence_analytics': confidence_stats
        })
        
    except Exception as e:
        logging.error(f"Admin prediction analytics error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to fetch prediction analytics: {str(e)}'
        }), 500
