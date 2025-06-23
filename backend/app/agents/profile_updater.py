from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import json

from app.config import settings
from app.agents.state import GraphState
from app.services.firebase_service import firebase_service

class ProfileUpdate(BaseModel):
    updates: Dict[str, Any] = Field(description="Profile fields to update")
    has_updates: bool = Field(description="Whether any updates were found")

class ProfileUpdater:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o-mini",
            temperature=0.1
        )
        
        self.parser = JsonOutputParser(pydantic_object=ProfileUpdate)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a profile update detector. Analyze user messages to identify new skills or experience they mention.

You can update these fields:
- skills: Add new skills mentioned (e.g., "I know Python", "I'm learning React")
- experience: Add new job info (only if they provide company AND title)
- about: Update professional summary if provided
- headline: Update if they provide a new professional title

Rules:
1. Only add NEW information not already in their profile
2. For skills: Look for "I know", "I can", "I'm learning", "I use", etc.
3. For experience: Need both company name and job title
4. Be conservative - don't guess or infer
5. If no new info, return has_updates: false and empty updates

{format_instructions}"""),
            ("human", """Current profile:
{current_profile}

User message:
{user_message}

Extract any profile updates:""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def update_profile(self, state: GraphState) -> GraphState:
        """Detect and apply profile updates from user message"""
        
        current_profile = state["user_profile_data"]
        user_message = state["current_user_query"]
        session_id = state["session_id"]
        
        try:
            # Check for profile updates
            result = self.chain.invoke({
                "current_profile": json.dumps(current_profile, default=str),
                "user_message": user_message,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            if result.get("has_updates", False):
                updates = result.get("updates", {})
                
                # Apply updates
                success = self._apply_updates(session_id, current_profile, updates)
                
                if success:
                    # Refresh profile data
                    updated_profile = firebase_service.get_user_profile(session_id)
                    if updated_profile:
                        state["user_profile_data"] = updated_profile
                    
                    state["profile_updated"] = True
                    state["profile_updates"] = {
                        "updates": updates,
                        "message": self._create_update_message(updates)
                    }
                    
                    # Check if user might want job recommendations after profile update
                    if "skills" in updates:
                        state["next_agent"] = "router"  # Let router decide if job_fit_analyst should be next
                else:
                    state["profile_updates"] = {
                        "updates": {},
                        "message": "I noted your information but couldn't update your profile right now."
                    }
            else:
                # No updates detected
                state["profile_updates"] = None
                # Since no profile update happened, maybe user needs another agent
                state["next_agent"] = "router"
        
        except Exception as e:
            print(f"Profile updater error: {e}")
            state["profile_updates"] = None
            state["next_agent"] = "router"
        
        state["agent_type"] = "profile_updater"
        return state
    
    def _apply_updates(self, session_id: str, current_profile: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Apply updates to the user profile"""
        try:
            final_updates = {}
            
            for field, value in updates.items():
                if field == "skills":
                    current_skills = set(current_profile.get("skills", []))
                    new_skills = value if isinstance(value, list) else [value]
                    current_skills.update(new_skills)
                    final_updates["skills"] = list(current_skills)
                
                elif field == "experience":
                    current_exp = current_profile.get("experience", [])
                    if isinstance(value, list):
                        current_exp.extend(value)
                    else:
                        current_exp.append(value)
                    final_updates["experience"] = current_exp
                
                else:
                    final_updates[field] = value
            
            return firebase_service.update_user_profile(session_id, final_updates)
        
        except Exception as e:
            print(f"Error applying updates: {e}")
            return False
    
    def _create_update_message(self, updates: Dict[str, Any]) -> str:
        """Create confirmation message for updates"""
        parts = ["✅ **Profile Updated!**\n"]
        
        if "skills" in updates:
            skills = updates["skills"]
            skill_list = ", ".join(skills[-3:]) if isinstance(skills, list) else skills
            parts.append(f"• Added skills: {skill_list}")
        
        if "experience" in updates:
            parts.append("• Updated work experience")
        
        if "about" in updates:
            parts.append("• Updated professional summary")
        
        parts.append("\nYour profile is now more complete! This helps me provide better career guidance.")
        
        return "\n".join(parts)

# Create agent instance
profile_updater = ProfileUpdater() 