#!/usr/bin/env python
"""
Script to create demo admin and test accounts for development and testing
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_config import create_user, get_user_by_email, get_db
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask

# Load environment variables
load_dotenv()

# Create Flask app for context
app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/medicine_db')

def create_demo_accounts():
    """Create demo accounts for testing"""
    
    print("🚀 Creating demo accounts for Medicine Prediction System...")
    
    # Demo accounts to create
    demo_accounts = [
        {
            'email': 'admin@medicine.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'profile': {
                'age': 30,
                'gender': 'Other',
                'phone': '+1234567890'
            }
        },
        {
            'email': 'doctor@medicine.com', 
            'password': 'doctor123',
            'first_name': 'Dr. John',
            'last_name': 'Doe',
            'role': 'doctor',
            'profile': {
                'age': 35,
                'gender': 'Male',
                'phone': '+1234567891'
            }
        },
        {
            'email': 'patient@medicine.com',
            'password': 'patient123', 
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'patient',
            'profile': {
                'age': 28,
                'gender': 'Female',
                'phone': '+1234567892'
            }
        }
    ]
    
    created_count = 0
    
    with app.app_context():
        for account in demo_accounts:
            try:
                # Check if user already exists
                existing_user = get_user_by_email(account['email'])
                if existing_user:
                    print(f"⚠️  User {account['email']} already exists - skipping")
                    continue
                
                # Create user data
                user_data = {
                    'email': account['email'],
                    'password_hash': generate_password_hash(account['password']),
                    'first_name': account['first_name'],
                    'last_name': account['last_name'],
                    'role': account['role'],
                    'profile': account['profile'],
                    'created_at': datetime.utcnow(),
                    'last_login': None,
                    'is_active': True
                }
                
                # Create user
                user_id = create_user(user_data)
                if user_id:
                    created_count += 1
                    print(f"✅ Created {account['role']} account: {account['email']} (password: {account['password']})")
                else:
                    print(f"❌ Failed to create account: {account['email']}")
                    
            except Exception as e:
                print(f"❌ Error creating {account['email']}: {str(e)}")
    
    print(f"\n🎉 Successfully created {created_count} demo accounts!")
    print("\nDemo Login Credentials:")
    print("=" * 50)
    for account in demo_accounts:
        print(f"👤 {account['role'].title()}: {account['email']} / {account['password']}")
    
    return created_count > 0

def test_database_connection():
    """Test database connection"""
    try:
        print("🔌 Testing database connection...")
        
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/medicine_db')
        client = MongoClient(mongo_uri)
        
        # Handle different URI formats
        if 'mongodb+srv://' in mongo_uri or mongo_uri.count('/') < 3:
            db_name = 'medicine_db'
        else:
            db_path = mongo_uri.split('/')[-1]
            db_name = db_path.split('?')[0] if '?' in db_path else db_path
            if not db_name:
                db_name = 'medicine_db'
        
        db = client[db_name]
        
        # Test the connection
        db.command('ping')
        
        print(f"✅ Connected to database: {db_name}")
        print(f"📊 Current user count: {db.users.count_documents({})}")
        print(f"📈 Current prediction count: {db.prediction_logs.count_documents({})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n💡 Make sure MongoDB is running and accessible!")
        return False

def create_sample_predictions():
    """Create some sample prediction logs for demo purposes"""
    try:
        print("\n📝 Creating sample prediction logs...")
        
        with app.app_context():
            db = get_db()
            if not db:
                print("❌ Cannot create sample data - no database connection")
                return False
            
            # Get admin user for sample data
            admin_user = get_user_by_email('admin@medicine.com')
            patient_user = get_user_by_email('patient@medicine.com')
            
            if not admin_user or not patient_user:
                print("⚠️  Demo users not found - cannot create sample predictions")
                return False
            
            sample_predictions = [
                {
                    'user_id': str(patient_user['_id']),
                    'symptoms': ['headache', 'fever', 'fatigue'],
                    'predicted_disease': 'Common Cold',
                    'confidence': 0.95,
                    'success': True,
                    'timestamp': datetime.utcnow(),
                    'metadata': {'source': 'demo_data'}
                },
                {
                    'user_id': str(patient_user['_id']),
                    'symptoms': ['cough', 'chest_pain', 'breathlessness'],
                    'predicted_disease': 'Bronchial Asthma',
                    'confidence': 0.88,
                    'success': True,
                    'timestamp': datetime.utcnow(),
                    'metadata': {'source': 'demo_data'}
                },
                {
                    'user_id': str(admin_user['_id']),
                    'symptoms': ['stomach_pain', 'nausea', 'vomiting'],
                    'predicted_disease': 'Gastroenteritis',
                    'confidence': 0.92,
                    'success': True,
                    'timestamp': datetime.utcnow(),
                    'metadata': {'source': 'demo_data'}
                }
            ]
            
            # Insert sample predictions
            result = db.prediction_logs.insert_many(sample_predictions)
            
            if result.inserted_ids:
                print(f"✅ Created {len(result.inserted_ids)} sample prediction logs")
                return True
            else:
                print("❌ Failed to create sample predictions")
                return False
            
    except Exception as e:
        print(f"❌ Error creating sample predictions: {str(e)}")
        return False

def main():
    """Main function"""
    print("🏥 Medicine Prediction System - Demo Account Creator")
    print("=" * 60)
    
    # Test database connection first
    if not test_database_connection():
        print("\n❌ Cannot proceed without database connection!")
        sys.exit(1)
    
    # Create demo accounts
    if create_demo_accounts():
        print("\n✨ Demo accounts created successfully!")
        
        # Create sample prediction data
        create_sample_predictions()
        
        print("\n🎯 You can now test the system with these accounts:")
        print("   • Admin dashboard: http://localhost:3000/admin")
        print("   • Patient dashboard: http://localhost:3000/dashboard") 
        print("   • Login page: http://localhost:3000/login")
    else:
        print("\n⚠️  No new accounts were created")

if __name__ == '__main__':
    main()
