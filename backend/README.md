# LearnTube AI Career Coach - Backend

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Create Environment File

Create a `.env` file in the backend directory with the following content:

```env
# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here
APIFY_API_TOKEN=your_apify_api_token_here

# Firebase Configuration
FIREBASE_PROJECT_ID=learntube-18ce5
FIREBASE_CREDENTIALS_PATH=../learntube-18ce5-firebase-adminsdk-fbsvc-8991def342.json
GOOGLE_APPLICATION_CREDENTIALS=../learntube-18ce5-firebase-adminsdk-fbsvc-8991def342.json

# Application Configuration
DEBUG=True
```

**Important:** Replace the API keys with your actual values:
- Get OPENROUTER_API_KEY from https://openrouter.ai/
- Get APIFY_API_TOKEN from https://apify.com/

### 3. Run the Backend

```bash
python run.py
```

The backend will start on http://localhost:8000

## API Endpoints

- `GET /` - Health check endpoint
- `POST /start_session` - Start a new career coaching session
- `POST /chat` - Send messages to the AI career coach
- `GET /profile/{session_id}` - Get user profile
- `GET /chat_history/{session_id}` - Get chat history

## Troubleshooting

If you encounter import errors or dependencies issues, make sure you:
1. Are using Python 3.13 or later
2. Have activated your virtual environment
3. Have created the `.env` file with valid API keys 