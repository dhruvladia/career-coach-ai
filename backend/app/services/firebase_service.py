import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import json

from app.config import settings
from app.models.schemas import UserProfile, Experience

class FirebaseService:
    def __init__(self):
        if not firebase_admin._apps:
            if settings.firebase_credentials_path:
                cred = credentials.Certificate(settings.firebase_credentials_path)
            else:
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred, {
                'projectId': settings.firebase_project_id,
            })
        
        self.db = firestore.client()
    
    def create_user_session(self, linkedin_url: str, profile_data: Dict[str, Any] = None) -> str:
        """Create a new user session and profile document"""
        session_id = str(uuid.uuid4())
        
        user_profile = {
            'session_id': session_id,
            'linkedin_url': linkedin_url,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        if profile_data:
            user_profile.update(profile_data)
        
        # Create the profile document
        self.db.collection('users').document(session_id).collection('profile').document('data').set(user_profile)
        
        return session_id
    
    def get_user_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile data"""
        try:
            doc = self.db.collection('users').document(session_id).collection('profile').document('data').get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def update_user_profile(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile with new data"""
        try:
            updates['updated_at'] = datetime.utcnow()
            
            profile_ref = self.db.collection('users').document(session_id).collection('profile').document('data')
            profile_ref.update(updates)
            
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def save_conversation_state(self, session_id: str, state_data: Dict[str, Any]) -> bool:
        """Save LangGraph conversation state"""
        try:
            state_ref = self.db.collection('users').document(session_id).collection('langgraph_memory').document('state')
            state_ref.set(state_data, merge=True)
            return True
        except Exception as e:
            print(f"Error saving conversation state: {e}")
            return False
    
    def get_conversation_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get LangGraph conversation state"""
        try:
            doc = self.db.collection('users').document(session_id).collection('langgraph_memory').document('state').get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting conversation state: {e}")
            return None
    
    def add_chat_history(self, session_id: str, message: str, response: str, agent_type: str) -> bool:
        """Add a chat message to history"""
        try:
            chat_data = {
                'message': message,
                'response': response,
                'agent_type': agent_type,
                'timestamp': datetime.utcnow()
            }
            
            self.db.collection('users').document(session_id).collection('chat_history').add(chat_data)
            return True
        except Exception as e:
            print(f"Error adding chat history: {e}")
            return False
    
    def get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent chat history"""
        try:
            query = (self.db.collection('users')
                    .document(session_id)
                    .collection('chat_history')
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

# Create a singleton instance
firebase_service = FirebaseService() 