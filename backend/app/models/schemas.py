from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime

class LinkedInProfileRequest(BaseModel):
    linkedin_url: str
    
class ChatMessage(BaseModel):
    session_id: str
    message: str
<<<<<<< HEAD
    resume_from_interrupt: bool = False  # Flag to indicate resuming from human interaction
=======
>>>>>>> fa29382d12c4f71e87bff507946ee59378543435
    
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
<<<<<<< HEAD
    requires_input: bool = False
    input_type: Optional[str] = None
    workflow_stage: str = "completed"
=======
>>>>>>> fa29382d12c4f71e87bff507946ee59378543435
    
class SessionResponse(BaseModel):
    session_id: str
    message: str
    profile_data: Optional[UserProfile] = None 