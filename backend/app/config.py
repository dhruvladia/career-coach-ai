import os
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    apify_api_token: str = os.getenv("APIFY_API_TOKEN", "")
    
    # Firebase Configuration
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Application Configuration
    app_title: str = "LearnTube AI Career Coach"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:8501", 
        "http://127.0.0.1:8501",
        "https://learntube-frontend.onrender.com",  # Production frontend URL
        "https://*.onrender.com"  # Allow all Render subdomains
    ]
    
    class Config:
        env_file = ".env"

settings = Settings() 