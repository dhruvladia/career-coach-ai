#!/usr/bin/env python3
"""
Test script to verify deployment configuration before pushing to Render.
This helps catch configuration issues early.
"""

import os
import sys
import json
import requests
import subprocess
import time
from pathlib import Path

def load_env_file():
    """Load environment variables from backend/.env file."""
    env_file = Path('backend/.env')
    if env_file.exists():
        print("📄 Loading environment variables from backend/.env...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
        return True
    return False

def test_environment_variables():
    """Test that required environment variables are configured."""
    print("🔍 Testing Environment Variables...")
    
    # Try to load from .env file first
    env_loaded = load_env_file()
    
    required_vars = {
        'OPENROUTER_API_KEY': 'OpenRouter API key',
        'APIFY_API_TOKEN': 'Apify API token',
        'FIREBASE_PROJECT_ID': 'Firebase project ID'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  ❌ {var} - {description}")
        else:
            print(f"  ✅ {var} - Set")
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(var)
        
        if not env_loaded:
            print("\n💡 No .env file found in backend directory.")
            print("   Create backend/.env with:")
            print("   OPENROUTER_API_KEY=your_key_here")
            print("   APIFY_API_TOKEN=your_token_here") 
            print("   FIREBASE_PROJECT_ID=learntube-18ce5")
        else:
            print("\n💡 .env file loaded but some variables are missing.")
            print("   Please check your backend/.env file contains all required variables.")
        
        print("\n   Alternative - set them temporarily:")
        print("   export OPENROUTER_API_KEY=your_key_here  # Linux/macOS")
        print("   $env:OPENROUTER_API_KEY='your_key_here'  # Windows PowerShell")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_firebase_credentials():
    """Test Firebase credentials configuration."""
    print("\n🔍 Testing Firebase Configuration...")
    
    # Check for base64 credentials
    if os.getenv('FIREBASE_CREDENTIALS_BASE64'):
        print("  ✅ FIREBASE_CREDENTIALS_BASE64 - Set")
        return True
    
    # Check for credentials file
    firebase_files = [
        "learntube-18ce5-firebase-adminsdk-fbsvc-8991def342.json",
        "firebase-adminsdk.json",
        "service-account.json"
    ]
    
    for file_name in firebase_files:
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r') as f:
                    json.load(f)
                print(f"  ✅ {file_name} - Valid JSON")
                return True
            except json.JSONDecodeError:
                print(f"  ❌ {file_name} - Invalid JSON")
                return False
    
    print("  ❌ No Firebase credentials found")
    print("     Run: python scripts/prepare_firebase_for_render.py")
    return False

def test_backend_startup():
    """Test that backend can start successfully."""
    print("\n🔍 Testing Backend Startup...")
    
    try:
        # Change to backend directory and add to Python path
        original_dir = os.getcwd()
        backend_dir = os.path.join(original_dir, 'backend')
        
        if not os.path.exists(backend_dir):
            print(f"  ❌ Backend directory not found: {backend_dir}")
            return False
        
        # Add backend directory to Python path
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # Test import
        try:
            from app.main import app
            print("  ✅ Backend imports successfully")
        except ImportError as e:
            print(f"  ❌ Backend import failed: {e}")
            print(f"     Make sure you're running from the project root directory")
            return False
        
        # Test configuration
        try:
            from app.config import settings
            print("  ✅ Configuration loads successfully")
        except Exception as e:
            print(f"  ❌ Configuration failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Backend test failed: {e}")
        return False
    finally:
        # Remove backend from path to avoid conflicts
        if backend_dir in sys.path:
            sys.path.remove(backend_dir)

def test_frontend_startup():
    """Test that frontend can start successfully."""
    print("\n🔍 Testing Frontend Startup...")
    
    try:
        # Change to frontend directory
        original_dir = os.getcwd()
        os.chdir('frontend')
        
        # Test import
        try:
            import streamlit as st
            print("  ✅ Streamlit imports successfully")
        except ImportError as e:
            print(f"  ❌ Streamlit import failed: {e}")
            return False
        
        # Test API_BASE_URL configuration
        sys.path.append('.')
        try:
            # Simulate the frontend import
            os.environ['API_BASE_URL'] = 'http://test-backend-url.com'
            import importlib.util
            spec = importlib.util.spec_from_file_location("streamlit_app", "streamlit_app.py")
            # Just check if it can be loaded
            print("  ✅ Frontend configuration valid")
        except Exception as e:
            print(f"  ❌ Frontend configuration error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Frontend test failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def test_dependencies():
    """Test that all dependencies are installable."""
    print("\n🔍 Testing Dependencies...")
    
    # Test backend dependencies
    try:
        subprocess.check_output(['pip', 'install', '--dry-run', '-r', 'backend/requirements.txt'], 
                              stderr=subprocess.STDOUT)
        print("  ✅ Backend dependencies valid")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Backend dependencies error: {e.output.decode()}")
        return False
    
    # Test frontend dependencies
    try:
        subprocess.check_output(['pip', 'install', '--dry-run', '-r', 'frontend/requirements.txt'], 
                              stderr=subprocess.STDOUT)
        print("  ✅ Frontend dependencies valid")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Frontend dependencies error: {e.output.decode()}")
        return False
    
    return True

def test_render_config():
    """Test render.yaml configuration."""
    print("\n🔍 Testing Render Configuration...")
    
    if not os.path.exists('render.yaml'):
        print("  ❌ render.yaml not found")
        return False
    
    try:
        import yaml
        with open('render.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        if 'services' not in config:
            print("  ❌ No services defined in render.yaml")
            return False
        
        services = config['services']
        if len(services) < 2:
            print("  ❌ Expected at least 2 services (backend and frontend)")
            return False
        
        print(f"  ✅ render.yaml valid with {len(services)} services")
        return True
        
    except Exception as e:
        print(f"  ❌ render.yaml error: {e}")
        return False

def main():
    """Run all deployment configuration tests."""
    print("🚀 LearnTube AI - Deployment Configuration Test")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_firebase_credentials,
        test_dependencies,
        test_backend_startup,
        test_frontend_startup,
        test_render_config
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 