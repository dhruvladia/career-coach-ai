from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime

class LinkedInProfileRequest(BaseModel):
    linkedin_url: str
    
class ChatMessage(BaseModel):
    session_id: str
    message: str
    
class Experience(BaseModel):
    title: str
    company: str
    duration: Optional[str] = None
    description: Optional[str] = None
    
class UserProfile(BaseModel):
    session_id: str
    linkedin_url: str
    name: Optional[str] = None
    about: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: Optional[List[Dict[str, Any]]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
class JobFitAnalysis(BaseModel):
    score: int
    summary: str
    missing_skills: List[str]
    enhancements: List[str]
    
class CareerPathResponse(BaseModel):
    analysis: str
    trajectory: str
    upskilling_areas: List[str]
    
class ChatResponse(BaseModel):
    message: str
    agent_type: str
    session_id: str
    profile_updated: bool = False
    job_fit_analysis: Optional[JobFitAnalysis] = None
    career_path: Optional[CareerPathResponse] = None
    
class SessionResponse(BaseModel):
    session_id: str
    message: str
    profile_data: Optional[UserProfile] = None 