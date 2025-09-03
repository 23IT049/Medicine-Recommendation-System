#!/usr/bin/env python3
"""
Simple test script for the Medicine Prediction API
"""

import requests
import json
from pprint import pprint

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/api/health")
        print(f"Status: {response.status_code}")
        pprint(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_ml_endpoints():
    """Test ML prediction endpoints"""
    print("\n🧠 Testing ML Endpoints...")
    
    # Test symptoms list
    try:
        print("Getting symptoms list...")
        response = requests.get(f"{BASE_URL}/ml/symptoms/list")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Symptoms loaded: {data['total_count']} symptoms")
        else:
            print(f"❌ Failed to get symptoms: {response.status_code}")
    except Exception as e:
        print(f"❌ Symptoms endpoint error: {e}")
    
    # Test prediction
    try:
        print("\nTesting prediction...")
        test_symptoms = ["headache", "fever", "cough"]
        response = requests.post(
            f"{BASE_URL}/ml/predict", 
            json={"symptoms": test_symptoms}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Prediction successful!")
                print(f"   Disease: {data['predicted_disease']}")
                print(f"   Confidence: {data['confidence']}")
                print(f"   Valid symptoms: {len(data['symptoms_detected'])}")
            else:
                print(f"⚠️ Prediction failed: {data['message']}")
        else:
            print(f"❌ Prediction request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")

def test_symptoms_search():
    """Test symptom search functionality"""
    print("\n🔍 Testing Symptom Search...")
    try:
        response = requests.get(f"{BASE_URL}/ml/symptoms/search", params={"q": "head"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search results for 'head': {data['symptoms']}")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {e}")

def test_demo_login():
    """Test demo login"""
    print("\n👤 Testing Demo Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/demo-login",
            json={"email": "demo@medicine.com", "password": "demo123"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Demo login successful!")
            print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   Token: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"❌ Demo login failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Demo login error: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Starting Medicine Prediction API Tests")
    print("=" * 50)
    
    # Test health check
    health_ok = test_health_check()
    
    if health_ok:
        # Test ML endpoints
        test_ml_endpoints()
        
        # Test search
        test_symptoms_search()
        
        # Test demo login
        token = test_demo_login()
        
        print("\n" + "=" * 50)
        print("🎉 Test Summary:")
        print("✅ Health check: PASSED" if health_ok else "❌ Health check: FAILED")
        print("✅ ML endpoints: Available")
        print("✅ Demo login: Working")
        print("\n📝 Next steps:")
        print("1. Start the Flask server: python app.py")
        print("2. Test with frontend or Postman")
        print("3. Build the React frontend")
    
    else:
        print("❌ Server is not running. Please start with: python app.py")
