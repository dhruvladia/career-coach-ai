# LearnTube AI Career Coach - Setup Guide

## Quick Start

### Backend Setup
1. Navigate to `backend/` directory
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with required API keys
6. Run: `python run.py`

### Frontend Setup
1. Navigate to `frontend/` directory
2. Install dependencies: `npm install`
3. Create `.env.local` file with Firebase config
4. Run: `npm start`

## Required API Keys

### Backend (.env)
```
OPENROUTER_API_KEY=sk-your-openrouter-key
APIFY_API_TOKEN=your-apify-token
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=path/to/serviceAccountKey.json
```

### Frontend (.env.local)
```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_FIREBASE_API_KEY=your-firebase-api-key
REACT_APP_FIREBASE_PROJECT_ID=your-firebase-project-id
```

## Service Setup

1. **OpenRouter**: Get API key from openrouter.ai
2. **Firebase**: Create project, enable Firestore, download service account key
3. **Apify**: Sign up, get API token for LinkedIn scraping

## Architecture

- Backend: FastAPI + LangGraph multi-agent system
- Frontend: React + Tailwind CSS
- Database: Google Firestore
- AI: 5 specialized agents (Router, Job Fit, Career Path, Profile Updater, Content Enhancement)

## Testing

Use public LinkedIn profiles for testing:
- https://linkedin.com/in/satyanadella
- https://linkedin.com/in/jeffweiner08

The application works even if LinkedIn scraping fails - users can manually share their background information. 