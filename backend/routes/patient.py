from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db_config import get_user_prediction_history, get_db, get_user_by_id
from datetime import datetime, timedelta
from bson import ObjectId

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get patient dashboard data with stats and recent activity"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
        # Get prediction history for stats
        predictions = get_user_prediction_history(user_id, limit=50)
        
        # Calculate stats
        total_predictions = len(predictions)
        
        # Last prediction timestamp
        last_prediction = 'Never'
        if total_predictions > 0:
            last_prediction = predictions[0].get('timestamp', datetime.utcnow())
        
        # Weekly predictions
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_predictions = len([p for p in predictions if p.get('timestamp', datetime.utcnow()) >= week_ago])
        
        # Calculate accuracy (if available)
        accuracy = 0
        accuracy_count = 0
        for p in predictions:
            if 'confidence' in p:
                accuracy += p['confidence']
                accuracy_count += 1
        
        avg_accuracy = round((accuracy / accuracy_count) * 100) if accuracy_count > 0 else 0
        
        # Generate recent activity
        recent_activity = []
        
        # Add account creation if recent
        if user.get('created_at'):
            days_since_creation = (datetime.utcnow() - user['created_at']).days
            if days_since_creation < 30:  # Show for first month
                recent_activity.append({
                    'type': 'account',
                    'message': 'Account created successfully',
                    'time': user['created_at'],
                    'time_display': format_time_ago(user['created_at'])
                })
        
        # Add recent predictions (latest 5)
        for p in predictions[:5]:
            recent_activity.append({
                'type': 'prediction',
                'message': f"Predicted {p.get('predicted_disease', 'Unknown')} with {round((p.get('confidence', 0) * 100))}% confidence",
                'time': p.get('timestamp', datetime.utcnow()),
                'time_display': format_time_ago(p.get('timestamp', datetime.utcnow()))
            })
        
        # Sort by time (most recent first)
        recent_activity.sort(key=lambda x: x['time'], reverse=True)
        
        # Format for display (convert datetime objects to string)
        for activity in recent_activity:
            activity['time'] = activity['time'].isoformat() if isinstance(activity['time'], datetime) else activity['time']
        
        return jsonify({
            'success': True,
            'stats': {
                'total_predictions': total_predictions,
                'last_prediction': last_prediction.isoformat() if isinstance(last_prediction, datetime) else last_prediction,
                'weekly_predictions': weekly_predictions,
                'accuracy': avg_accuracy
            },
            'recent_activity': recent_activity[:10]  # Limit to 10 items
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch dashboard data: {str(e)}'
        }), 500

@patient_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get patient prediction history"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 20))  # Default 20, can be adjusted via query params
        
        # Get user to check if they exist
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get prediction history
        predictions = get_user_prediction_history(user_id, limit=limit)
        
        # Format predictions for response
        formatted_predictions = []
        for p in predictions:
            # Convert ObjectId to string for JSON serialization
            if '_id' in p:
                p['_id'] = str(p['_id'])
            
            # Format timestamp
            if 'timestamp' in p and isinstance(p['timestamp'], datetime):
                p['timestamp'] = p['timestamp'].isoformat()
                
            # Format user_id if present
            if 'user_id' in p and not isinstance(p['user_id'], str):
                p['user_id'] = str(p['user_id'])
                
            formatted_predictions.append(p)
        
        return jsonify({
            'success': True,
            'predictions': formatted_predictions,
            'count': len(formatted_predictions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch history: {str(e)}'
        }), 500

@patient_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """Get patient's recent activity"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 10))  # Default 10, can be adjusted
        
        # Get user info
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
        # Get prediction history
        predictions = get_user_prediction_history(user_id, limit=limit)
        
        # Format activities
        activities = []
        
        # Add account creation activity if recent
        if user.get('created_at'):
            days_since_creation = (datetime.utcnow() - user['created_at']).days
            if days_since_creation < 30:  # Show for first month
                activities.append({
                    'type': 'account',
                    'message': 'Account created successfully',
                    'time': user['created_at'].isoformat(),
                    'time_display': format_time_ago(user['created_at'])
                })
        
        # Add recent predictions
        for p in predictions:
            timestamp = p.get('timestamp', datetime.utcnow())
            activities.append({
                'type': 'prediction',
                'id': str(p.get('_id')),
                'message': f"Predicted {p.get('predicted_disease', 'Unknown')}",
                'details': f"Confidence: {round((p.get('confidence', 0) * 100))}%",
                'time': timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
                'time_display': format_time_ago(timestamp)
            })
        
        # Sort by time (most recent first)
        activities.sort(key=lambda x: x['time'], reverse=True)
        
        return jsonify({
            'success': True,
            'activities': activities[:limit],
            'count': len(activities[:limit])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch recent activity: {str(e)}'
        }), 500

def format_time_ago(timestamp):
    """Format timestamp as a human-readable 'time ago' string"""
    if not timestamp:
        return 'Unknown time'
    
    if not isinstance(timestamp, datetime):
        try:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                return 'Unknown time'
        except:
            return 'Unknown time'
    
    now = datetime.utcnow()
    diff = now - timestamp
    
    # Less than a minute
    if diff.total_seconds() < 60:
        return 'Just now'
    
    # Less than an hour
    if diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    
    # Less than a day
    if diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    
    # Less than a week
    if diff.total_seconds() < 604800:
        days = int(diff.total_seconds() / 86400)
        return f"{days} {'day' if days == 1 else 'days'} ago"
    
    # Less than a month
    if diff.total_seconds() < 2592000:
        weeks = int(diff.total_seconds() / 604800)
        return f"{weeks} {'week' if weeks == 1 else 'weeks'} ago"
    
    # More than a month
    months = int(diff.total_seconds() / 2592000)
    if months < 12:
        return f"{months} {'month' if months == 1 else 'months'} ago"
    
    # Years
    years = int(months / 12)
    return f"{years} {'year' if years == 1 else 'years'} ago"
