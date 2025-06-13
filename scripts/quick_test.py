#!/usr/bin/env python3
"""
Quick deployment readiness test - skips environment variables check.
This validates the core deployment configuration without requiring API keys.
"""

import os
import sys
import json
import subprocess

def test_firebase_credentials():
    """Test Firebase credentials configuration."""
    print("🔍 Testing Firebase Configuration...")
    
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

def test_file_structure():
    """Test that required files exist."""
    print("\n🔍 Testing File Structure...")
    
    required_files = [
        'render.yaml',
        'runtime.txt',
        'backend/requirements.txt',
        'frontend/requirements.txt',
        'backend/app/main.py',
        'frontend/streamlit_app.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            missing_files.append(f"  ❌ {file_path}")
    
    if missing_files:
        print("\n❌ Missing required files:")
        for file_path in missing_files:
            print(file_path)
        return False
    
    print("✅ All required files present")
    return True

def test_dependencies():
    """Test that all dependencies are installable."""
    print("\n🔍 Testing Dependencies...")
    
    # Test backend dependencies
    try:
        result = subprocess.run(['pip', 'install', '--dry-run', '-r', 'backend/requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Backend dependencies valid")
        else:
            print(f"  ❌ Backend dependencies error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ⚠️ Could not test backend dependencies: {e}")
    
    # Test frontend dependencies
    try:
        result = subprocess.run(['pip', 'install', '--dry-run', '-r', 'frontend/requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Frontend dependencies valid")
        else:
            print(f"  ❌ Frontend dependencies error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ⚠️ Could not test frontend dependencies: {e}")
    
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

def test_configuration_files():
    """Test configuration file contents."""
    print("\n🔍 Testing Configuration Files...")
    
    # Test runtime.txt
    try:
        with open('runtime.txt', 'r') as f:
            python_version = f.read().strip()
        if python_version.startswith('python-'):
            print(f"  ✅ runtime.txt - {python_version}")
        else:
            print(f"  ❌ runtime.txt - Invalid format: {python_version}")
            return False
    except Exception as e:
        print(f"  ❌ runtime.txt error: {e}")
        return False
    
    # Test backend configuration
    try:
        backend_dir = os.path.join(os.getcwd(), 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        from app.config import Settings
        settings = Settings()
        print("  ✅ Backend configuration loads")
        
        if backend_dir in sys.path:
            sys.path.remove(backend_dir)
    except Exception as e:
        print(f"  ❌ Backend configuration error: {e}")
        return False
    
    return True

def main():
    """Run deployment readiness tests."""
    print("🚀 LearnTube AI - Quick Deployment Readiness Test")
    print("=" * 55)
    print("ℹ️  Skipping environment variables check for quick validation")
    print()
    
    tests = [
        test_file_structure,
        test_firebase_credentials,
        test_render_config,
        test_configuration_files,
        test_dependencies
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
    
    print("\n" + "=" * 55)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 Core deployment configuration is ready!")
        print("💡 Next steps:")
        print("   1. Prepare Firebase credentials: python scripts/prepare_firebase_for_render.py")
        print("   2. Set up environment variables on Render")
        print("   3. Deploy to Render using render.yaml")
        return 0
    else:
        print("❌ Some configuration issues found. Please fix before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 