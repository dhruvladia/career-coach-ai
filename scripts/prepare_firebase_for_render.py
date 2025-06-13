#!/usr/bin/env python3
"""
Utility script to prepare Firebase credentials for Render deployment.
This script converts the Firebase service account JSON to base64 format
that can be safely used as an environment variable.
"""

import json
import base64
import os

def encode_firebase_credentials():
    """Convert Firebase service account JSON to base64 for Render deployment."""
    
    # Look for Firebase credentials file
    firebase_files = [
        "learntube-18ce5-firebase-adminsdk-fbsvc-8991def342.json",
        "firebase-adminsdk.json",
        "service-account.json"
    ]
    
    firebase_file = None
    for file_name in firebase_files:
        if os.path.exists(file_name):
            firebase_file = file_name
            break
    
    if not firebase_file:
        print("❌ Firebase credentials file not found!")
        print("Please ensure one of these files exists in the project root:")
        for file_name in firebase_files:
            print(f"  - {file_name}")
        return
    
    try:
        # Read and validate JSON
        with open(firebase_file, 'r') as f:
            credentials_data = json.load(f)
        
        # Validate required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in credentials_data]
        
        if missing_fields:
            print(f"❌ Invalid Firebase credentials file. Missing fields: {', '.join(missing_fields)}")
            return
        
        # Convert to JSON string and encode as base64
        json_string = json.dumps(credentials_data, separators=(',', ':'))
        base64_encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        
        print("✅ Firebase credentials successfully encoded!")
        print("\n📋 Copy this value to your Render environment variables:")
        print("Variable name: FIREBASE_CREDENTIALS_BASE64")
        print("Variable value:")
        print(f"{base64_encoded}")
        
        print(f"\n💡 Tips:")
        print("1. Go to your Render service dashboard")
        print("2. Navigate to Environment tab")
        print("3. Add new environment variable:")
        print("   - Key: FIREBASE_CREDENTIALS_BASE64")
        print("   - Value: (paste the encoded string above)")
        print("4. Save and redeploy your service")
        
        # Save to a file for reference
        with open('firebase_credentials_base64.txt', 'w') as f:
            f.write(base64_encoded)
        
        print(f"\n📄 Encoded credentials also saved to: firebase_credentials_base64.txt")
        print("⚠️  Remember to add this file to .gitignore for security!")
        
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {firebase_file}")
    except Exception as e:
        print(f"❌ Error processing Firebase credentials: {e}")

if __name__ == "__main__":
    print("🔧 Firebase Credentials Encoder for Render Deployment")
    print("=" * 55)
    encode_firebase_credentials() 