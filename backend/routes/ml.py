from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.ml_model import MedicinePredictor
from utils.validators import validate_symptoms
from datetime import datetime
import logging

ml_bp = Blueprint('ml', __name__)

# Initialize predictor once when module loads
try:
    predictor = MedicinePredictor()
    print("✓ ML Predictor initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize ML Predictor: {e}")
    predictor = None

@ml_bp.route('/predict', methods=['POST'])
def predict_medicine():
    """Main prediction endpoint - works without authentication for demo purposes"""
    if not predictor:
        return jsonify({
            'success': False,
            'message': 'ML model not available',
            'error': 'Predictor not initialized'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        symptoms = data.get('symptoms', [])
        
        # Validate input
        if not symptoms or not isinstance(symptoms, list):
            return jsonify({
                'success': False,
                'message': 'Symptoms list is required and must be an array'
            }), 400
        
        if len(symptoms) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one symptom is required'
            }), 400
        
        # Get prediction
        result = predictor.get_prediction_with_details(symptoms)
        
        # Add metadata
        result['timestamp'] = datetime.now().isoformat()
        result['model_version'] = '1.0.0'
        
        # Log prediction to database
        logging.info(f"Prediction made: {symptoms} -> {result.get('predicted_disease', 'N/A')}")
        
        # Save to database if available (for anonymous predictions)
        try:
            from utils.db_config import save_prediction_log
            if result.get('success'):
                save_prediction_log(
                    user_id='anonymous',
                    symptoms=symptoms,
                    prediction_result=result,
                    metadata={'source': 'anonymous_prediction', 'ip_address': request.remote_addr}
                )
        except Exception as e:
            logging.warning(f"Failed to save anonymous prediction log: {e}")
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error during prediction',
            'error': str(e)
        }), 500

@ml_bp.route('/predict-authenticated', methods=['POST'])
@jwt_required()
def predict_medicine_authenticated():
    """Authenticated prediction endpoint for logged-in users"""
    if not predictor:
        return jsonify({
            'success': False,
            'message': 'ML model not available'
        }), 500
    
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        
        # Validate input
        if not symptoms or not isinstance(symptoms, list):
            return jsonify({
                'success': False,
                'message': 'Symptoms list is required'
            }), 400
        
        # Get prediction
        result = predictor.get_prediction_with_details(symptoms)
        
        # Add user context
        result['user_id'] = user_id
        result['timestamp'] = datetime.now().isoformat()
        
        # Save to database for history
        try:
            from utils.db_config import save_prediction_log
            if result.get('success'):
                prediction_id = save_prediction_log(
                    user_id=user_id,
                    symptoms=symptoms,
                    prediction_result=result,
                    metadata={
                        'source': 'authenticated_prediction',
                        'ip_address': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent')
                    }
                )
                if prediction_id:
                    result['prediction_id'] = prediction_id
                    logging.info(f"Prediction saved with ID: {prediction_id}")
        except Exception as e:
            logging.error(f"Failed to save prediction log: {e}")
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@ml_bp.route('/symptoms/list', methods=['GET'])
def get_symptoms_list():
    """Get list of all possible symptoms"""
    if not predictor:
        return jsonify({
            'success': False,
            'message': 'ML model not available'
        }), 500
    
    try:
        symptoms_list = predictor.get_all_symptoms()
        return jsonify({
            'success': True,
            'symptoms': sorted(symptoms_list),  # Sort alphabetically
            'total_count': len(symptoms_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching symptoms',
            'error': str(e)
        }), 500

@ml_bp.route('/symptoms/search', methods=['GET'])
def search_symptoms():
    """Search symptoms by partial match"""
    if not predictor:
        return jsonify({
            'success': False,
            'message': 'ML model not available'
        }), 500
    
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 50)  # Max 50 results
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query parameter "q" is required'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'success': False,
                'message': 'Query must be at least 2 characters long'
            }), 400
        
        matching_symptoms = predictor.search_symptoms(query, limit)
        
        return jsonify({
            'success': True,
            'query': query,
            'symptoms': matching_symptoms,
            'count': len(matching_symptoms)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error searching symptoms',
            'error': str(e)
        }), 500

@ml_bp.route('/diseases/list', methods=['GET'])
def get_diseases_list():
    """Get list of all possible diseases"""
    if not predictor:
        return jsonify({
            'success': False,
            'message': 'ML model not available'
        }), 500
    
    try:
        diseases_list = predictor.get_all_diseases()
        return jsonify({
            'success': True,
            'diseases': sorted(diseases_list),
            'total_count': len(diseases_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching diseases',
            'error': str(e)
        }), 500

@ml_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """Get model information and performance metrics"""
    if not predictor:
        return jsonify({
            'success': False,
            'message': 'ML model not available'
        }), 500
    
    try:
        return jsonify({
            'success': True,
            'model_info': {
                'type': 'Support Vector Classifier (SVC)',
                'kernel': 'linear',
                'accuracy': 1.0,  # 100% accuracy from your notebook
                'total_symptoms': len(predictor.symptoms_dict),
                'total_diseases': len(predictor.diseases_list),
                'training_samples': 4920,
                'features': 132,
                'version': '1.0.0',
                'last_trained': '2024-01-01'  # Update with actual date
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching model info',
            'error': str(e)
        }), 500

@ml_bp.route('/validate-symptoms', methods=['POST'])
def validate_symptoms_endpoint():
    """Validate if provided symptoms exist in the model"""
    if not predictor:
        return jsonify({
            'success': False,
            'message': 'ML model not available'
        }), 500
    
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        
        if not isinstance(symptoms, list):
            return jsonify({
                'success': False,
                'message': 'Symptoms must be provided as an array'
            }), 400
        
        valid_symptoms = []
        invalid_symptoms = []
        suggestions = {}
        
        for symptom in symptoms:
            symptom = symptom.strip()
            if symptom in predictor.symptoms_dict:
                valid_symptoms.append(symptom)
            else:
                invalid_symptoms.append(symptom)
                # Find similar symptoms
                similar = predictor.search_symptoms(symptom, 3)
                if similar:
                    suggestions[symptom] = similar
        
        return jsonify({
            'success': True,
            'valid_symptoms': valid_symptoms,
            'invalid_symptoms': invalid_symptoms,
            'suggestions': suggestions,
            'validation_summary': {
                'total': len(symptoms),
                'valid': len(valid_symptoms),
                'invalid': len(invalid_symptoms)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error validating symptoms',
            'error': str(e)
        }), 500

# Health check for ML service
@ml_bp.route('/health', methods=['GET'])
def ml_health_check():
    """Health check for ML prediction service"""
    try:
        if not predictor:
            return jsonify({
                'status': 'unhealthy',
                'message': 'ML predictor not initialized',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # Quick test prediction
        test_symptoms = ['headache', 'fever']
        test_result = predictor.get_prediction_with_details(test_symptoms)
        
        return jsonify({
            'status': 'healthy',
            'message': 'ML prediction service is operational',
            'test_prediction': test_result.get('success', False),
            'model_loaded': True,
            'symptoms_count': len(predictor.symptoms_dict),
            'diseases_count': len(predictor.diseases_list),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': 'ML service error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503
