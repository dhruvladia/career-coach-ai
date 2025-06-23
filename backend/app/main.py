from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, Any

from app.config import settings
from app.models.schemas import (
    LinkedInProfileRequest,
    ChatMessage,
    ChatResponse,
    SessionResponse,
    UserProfile
)
from app.services.firebase_service import firebase_service
from app.services.linkedin_scraper import linkedin_scraper
from app.agents.langgraph_orchestrator import orchestrator # Ensure this import is correct

# Create FastAPI app
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="AI-powered career coaching application with LinkedIn profile analysis"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LearnTube AI Career Coach API",
        "version": settings.app_version,
        "status": "running"
    }

@app.post("/start_session", response_model=SessionResponse)
async def start_session(request: LinkedInProfileRequest):
    """
    Start a new career coaching session by scraping LinkedIn profile
    """
    try:
        linkedin_url = request.linkedin_url.strip()

        # Validate LinkedIn URL
        if not linkedin_url or "linkedin.com" not in linkedin_url:
            raise HTTPException(
                status_code=400,
                detail="Please provide a valid LinkedIn profile URL"
            )

        # Scrape LinkedIn profile
        print(f"Scraping LinkedIn profile: {linkedin_url}")
        profile_data = linkedin_scraper.scrape_profile(linkedin_url)

        if not profile_data:
            # Create session without scraped data - allow manual profile building
            session_id = firebase_service.create_user_session(linkedin_url)

            return SessionResponse(
                session_id=session_id,
                message="""Welcome to your AI Career Coach! 🚀

I wasn't able to automatically scrape your LinkedIn profile, but that's okay! I can still help you with:

✅ **Career guidance and planning**
✅ **Job fit analysis (just paste job descriptions)**
✅ **LinkedIn profile content improvement**
✅ **Skills development recommendations**

You can also manually share your background information with me, and I'll update your profile as we chat.

**To get started, try asking:**
- "Help me analyze this job description..." (paste the JD)
- "I'm a software engineer with 3 years experience, what should I focus on?"
- "How can I transition from X to Y role?"

What would you like to work on today?""",
                profile_data=None
            )

        # Create session with scraped profile data
        session_id = firebase_service.create_user_session(linkedin_url, profile_data)

        # Create welcome message based on profile
        welcome_message = f"""Welcome to your AI Career Coach, {profile_data.get('name', 'there')}! 🚀

I've analyzed your LinkedIn profile and I'm ready to help you with:

✅ **Job Fit Analysis** - Paste any job description for detailed compatibility analysis
✅ **Career Path Guidance** - Get personalized advice for your career goals
✅ **Profile Enhancement** - Improve your LinkedIn content for better visibility
✅ **Skills Development** - Identify key areas for growth

**Your Profile Summary:**
• **Role:** {profile_data.get('headline', 'Not specified')}
• **Skills:** {len(profile_data.get('skills', []))} skills identified
• **Experience:** {len(profile_data.get('experience', []))} positions

**To get started, try asking:**
- "Analyze this job description for me..." (paste the JD)
- "How can I improve my LinkedIn headline?"
- "What career path should I pursue?"
- "I also know [skill name]" (to update your profile)

What would you like to work on today?"""

        # Convert to UserProfile format for response
        user_profile = UserProfile(
            session_id=session_id,
            linkedin_url=linkedin_url,
            name=profile_data.get('name'),
            about=profile_data.get('about'),
            skills=profile_data.get('skills', []),
            experience=[{
                'title': exp.get('title', ''),
                'company': exp.get('company', ''),
                'duration': exp.get('duration'),
                'description': exp.get('description')
            } for exp in profile_data.get('experience', [])],
            education=profile_data.get('education', [])
        )

        return SessionResponse(
            session_id=session_id,
            message=welcome_message,
            profile_data=user_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to start session. Please try again."
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    Process a chat message through the AI career coaching system
    """
    try:
        session_id = request.session_id.strip()
        message = request.message.strip()

        if not session_id or not message:
            raise HTTPException(
                status_code=400,
                detail="Session ID and message are required"
            )

        # Get user profile
        user_profile = firebase_service.get_user_profile(session_id)
        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please start a new session."
            )

        # **** IMPORTANT: Orchestrator invocation was missing. Adding it here. ****
        # This is where the LangGraph workflow is initiated and 'result' is populated.
        result = orchestrator.process_message(
            session_id=session_id,
            user_message=message,
            user_profile=user_profile,
            resume_from_interrupt=request.dict().get("resume_from_interrupt", False)
        )
        
        return ChatResponse(
            message=result["message"],
            agent_type=result["agent_type"],
            session_id=session_id,
            profile_updated=result.get("profile_updated", False),
            job_fit_analysis=result.get("job_fit_analysis"),
            career_path=result.get("career_path"),
            requires_input=result.get("requires_input", False),
            input_type=result.get("input_type"),
            workflow_stage=result.get("workflow_stage", "completed")
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process message. Please try again."
        )

@app.get("/profile/{session_id}")
async def get_profile(session_id: str):
    """
    Get user profile data for a session
    """
    try:
        profile = firebase_service.get_user_profile(session_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        return profile

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve profile"
        )

@app.get("/chat_history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 10):
    """
    Get chat history for a session
    """
    try:
        history = firebase_service.get_chat_history(session_id, limit)
        return {"chat_history": history}

    except Exception as e:
        print(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat history"
        )

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    print(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug
    )
