# Medicine Prediction System - Backend API

A Flask-based REST API that uses Machine Learning to predict diseases based on symptoms.

## Features

🧠 **Machine Learning Prediction**
- 100% accuracy SVC model trained on 4,920 medical samples
- Support for 132 symptoms and 41 diseases
- Real-time disease prediction with detailed recommendations

🔐 **Authentication & Security**
- JWT-based authentication
- User registration and login
- Role-based access control (Patient, Doctor, Admin)
- Demo login for testing

📊 **Comprehensive Medical Data**
- Disease descriptions and precautions
- Medication recommendations
- Diet suggestions
- Workout/lifestyle recommendations

🔍 **Smart Search & Validation**
- Symptom search and autocomplete
- Input validation with suggestions
- Error handling and logging

## Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Setup ML Assets

Ensure these files are in the `ml_assets/` directory:
- `svc.pkl` (trained ML model)
- `symptoms_df.csv` (symptoms data)
- `description.csv` (disease descriptions)
- `medications.csv` (medication data)
- `precautions_df.csv` (precautions data)
- `workout_df.csv` (workout recommendations)
- `diets.csv` (diet recommendations)

### 3. Run the Server

**Option 1: Using the startup script (Recommended)**
```bash
python run.py
```

**Option 2: Direct Flask run**
```bash
python app.py
```

### 4. Test the API

```bash
# Test using the test script
python test_api.py
```

## API Endpoints

### 🏥 Health & Info
- `GET /api/health` - Health check
- `GET /api/ml/model/info` - Model information

### 🧠 Machine Learning
- `POST /api/ml/predict` - Disease prediction
- `GET /api/ml/symptoms/list` - Get all symptoms
- `GET /api/ml/symptoms/search?q=term` - Search symptoms
- `GET /api/ml/diseases/list` - Get all diseases
- `POST /api/ml/validate-symptoms` - Validate symptoms

### 👤 Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/demo-login` - Demo login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

## API Usage Examples

### 1. Disease Prediction

```bash
curl -X POST http://localhost:5000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["headache", "fever", "cough"]
  }'
```

**Response:**
```json
{
  "success": true,
  "predicted_disease": "Common Cold",
  "confidence": 1.0,
  "description": "Common Cold is a viral infection of the upper respiratory tract.",
  "precautions": ["rest", "drink fluids", "avoid cold", "keep warm"],
  "medications": ["Antipyretics", "Decongestants", "Cough suppressants"],
  "diet": ["Warm fluids", "Vitamin C rich foods"],
  "workout": ["Rest", "Light walking when better"],
  "symptoms_detected": ["headache", "fever", "cough"],
  "timestamp": "2024-08-23T09:45:00Z"
}
```

### 2. Demo Login

```bash
curl -X POST http://localhost:5000/api/auth/demo-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@medicine.com",
    "password": "demo123"
  }'
```

### 3. Search Symptoms

```bash
curl "http://localhost:5000/api/ml/symptoms/search?q=head"
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# MongoDB Configuration (optional)
MONGO_URI=mongodb://localhost:27017/medicine_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
```

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── run.py                 # Startup script
├── test_api.py            # API testing script
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── models/
│   ├── __init__.py
│   └── ml_model.py        # ML model wrapper
├── routes/
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   ├── ml.py              # ML prediction routes
│   ├── patient.py         # Patient routes
│   └── admin.py           # Admin routes
├── utils/
│   ├── __init__.py
│   ├── db_config.py       # Database configuration
│   └── validators.py      # Input validators
└── ml_assets/
    ├── svc.pkl            # Trained ML model
    ├── Training.csv       # Training data
    ├── symptoms_df.csv    # Symptoms data
    ├── description.csv    # Disease descriptions
    ├── medications.csv    # Medication data
    ├── precautions_df.csv # Precautions data
    ├── workout_df.csv     # Workout data
    └── diets.csv          # Diet data
```

## Machine Learning Model

### Model Details
- **Type**: Support Vector Classifier (SVC)
- **Kernel**: Linear
- **Accuracy**: 100% on test data
- **Training Samples**: 4,920
- **Features**: 132 symptoms
- **Diseases**: 41 different conditions

### Supported Symptoms (132 total)
- Common: headache, fever, cough, fatigue, nausea, dizziness
- Specific: chest_pain, abdominal_pain, joint_pain, muscle_weakness
- Advanced: yellowing_of_eyes, blood_in_sputum, altered_sensorium

### Supported Diseases (41 total)
- Infections: Common Cold, Flu, Pneumonia, Malaria, Dengue
- Chronic: Diabetes, Hypertension, Arthritis, Asthma
- Serious: Heart Attack, Paralysis, AIDS, Tuberculosis

## Development

### Adding New Endpoints

1. Create route in appropriate file (`routes/`)
2. Add validation using `utils/validators.py`
3. Update tests in `test_api.py`
4. Document in README

### Database Integration

The system supports MongoDB for user management and analytics:

```python
# Enable database features
MONGO_URI=mongodb://localhost:27017/medicine_db
```

## Testing

### Run Tests

```bash
# Test all endpoints
python test_api.py

# Test ML model only
python -c "from models.ml_model import MedicinePredictor; p = MedicinePredictor(); print('✅ Model OK')"
```

### Manual Testing with Postman

Import the API endpoints using:
- Base URL: `http://localhost:5000/api`
- Add `Content-Type: application/json` header
- Use demo login to get JWT token

## Deployment

### Production Setup

1. **Environment Variables**
   ```env
   FLASK_ENV=production
   JWT_SECRET_KEY=strong-production-key
   MONGO_URI=mongodb://prod-server:27017/medicine_db
   ```

2. **WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Docker Deployment**
   ```dockerfile
   FROM python:3.9
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   CMD ["python", "run.py"]
   ```

## Troubleshooting

### Common Issues

1. **ML Model Not Loading**
   - Ensure `svc.pkl` is in `ml_assets/` directory
   - Check file permissions
   - Verify scikit-learn version compatibility

2. **Missing CSV Files**
   - Copy all CSV files to `ml_assets/`
   - Check file names match exactly

3. **Import Errors**
   - Install requirements: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **Port Already in Use**
   - Change port in `.env` file
   - Or kill existing process: `lsof -ti:5000 | xargs kill`

### Debug Mode

```bash
FLASK_DEBUG=True python app.py
```

## API Response Formats

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error": "Technical details"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is for educational and research purposes.

## Support

For issues and questions:
- Check the troubleshooting section
- Run `python test_api.py` for diagnostics
- Review server logs for errors

---

🏥 **Medicine Prediction System** - Powered by Machine Learning
