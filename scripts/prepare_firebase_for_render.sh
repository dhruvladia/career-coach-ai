#!/bin/bash

# Firebase Credentials Encoder for Render Deployment
# This script converts the Firebase service account JSON to base64 format

echo "🔧 Firebase Credentials Encoder for Render Deployment"
echo "======================================================="

# Look for Firebase credentials file
FIREBASE_FILES=(
    "learntube-18ce5-firebase-adminsdk-fbsvc-8991def342.json"
    "firebase-adminsdk.json"
    "service-account.json"
)

FIREBASE_FILE=""
for file in "${FIREBASE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        FIREBASE_FILE="$file"
        break
    fi
done

if [[ -z "$FIREBASE_FILE" ]]; then
    echo "❌ Firebase credentials file not found!"
    echo "Please ensure one of these files exists in the project root:"
    for file in "${FIREBASE_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo "📄 Found Firebase credentials file: $FIREBASE_FILE"

# Validate JSON structure
if ! python3 -m json.tool "$FIREBASE_FILE" > /dev/null 2>&1; then
    echo "❌ Invalid JSON in $FIREBASE_FILE"
    exit 1
fi

# Check for required fields
REQUIRED_FIELDS=("type" "project_id" "private_key_id" "private_key" "client_email")
for field in "${REQUIRED_FIELDS[@]}"; do
    if ! grep -q "\"$field\"" "$FIREBASE_FILE"; then
        echo "❌ Missing required field: $field"
        exit 1
    fi
done

# Encode to base64
BASE64_ENCODED=$(cat "$FIREBASE_FILE" | base64 -w 0)

echo "✅ Firebase credentials successfully encoded!"
echo ""
echo "📋 Copy this value to your Render environment variables:"
echo "Variable name: FIREBASE_CREDENTIALS_BASE64"
echo "Variable value:"
echo "$BASE64_ENCODED"

# Save to file
echo "$BASE64_ENCODED" > firebase_credentials_base64.txt

echo ""
echo "💡 Tips:"
echo "1. Go to your Render service dashboard"
echo "2. Navigate to Environment tab"
echo "3. Add new environment variable:"
echo "   - Key: FIREBASE_CREDENTIALS_BASE64"
echo "   - Value: (paste the encoded string above)"
echo "4. Save and redeploy your service"
echo ""
echo "📄 Encoded credentials also saved to: firebase_credentials_base64.txt"
echo "⚠️  Remember to add this file to .gitignore for security!" 