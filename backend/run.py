#!/usr/bin/env python3
"""
Startup script for Medicine Prediction System Backend
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        print("✅ All required packages are available")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        return False

def install_requirements():
    """Install requirements from requirements.txt"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False
    else:
        print("❌ requirements.txt not found")
        return False

def check_ml_assets():
    """Check if ML assets are available"""
    ml_assets_dir = Path(__file__).parent / "ml_assets"
    required_files = ["svc.pkl", "symtoms_df.csv", "description.csv", "medications.csv"]
    
    missing_files = []
    for file in required_files:
        if not (ml_assets_dir / file).exists():
            # Also check root directory
            root_file = Path(__file__).parent.parent / file
            if not root_file.exists():
                missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing ML assets: {missing_files}")
        print("   Make sure to copy all CSV files and svc.pkl to ml_assets/ directory")
        return False
    
    print("✅ All ML assets are available")
    return True

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting Medicine Prediction System Backend...")
    print("📡 Server will be available at: http://localhost:5000")
    print("📊 API Documentation: http://localhost:5000/api/health")
    print("🔬 ML Endpoints: http://localhost:5000/api/ml/")
    print("\n👋 Press Ctrl+C to stop the server\n")
    
    try:
        # Import and run the app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main startup function"""
    print("🏥 Medicine Prediction System - Backend Startup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check requirements
    if not check_requirements():
        print("\n📦 Installing missing requirements...")
        if not install_requirements():
            print("❌ Failed to install requirements. Please run: pip install -r requirements.txt")
            sys.exit(1)
    
    # Check ML assets
    if not check_ml_assets():
        print("\n📁 Please ensure all ML assets are in the ml_assets/ directory:")
        print("   - svc.pkl (trained model)")
        print("   - *.csv files (symptoms, descriptions, medications, etc.)")
        sys.exit(1)
    
    print("\n✅ All checks passed!")
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
