from typing import Dict, List, Optional, Any, TypedDict
from langchain_core.messages import BaseMessage
import operator
from typing_extensions import Annotated

class GraphState(TypedDict):
    """State object for the LangGraph multi-agent system"""
    
    # Session and user data
    session_id: str
    user_profile_data: Dict[str, Any]
    current_user_query: str
    
    # Chat history and context
    chat_history: Annotated[List[BaseMessage], operator.add]
    
    # Agent workflow control
    agent_type: str  # Current agent handling the request
    next_agent: Optional[str]  # Next agent to route to
    
    # Agent outputs and scratchpad
    agent_scratchpad: Dict[str, Any]
    router_decision: str
    
    # Specialized outputs
    job_fit_analysis: Optional[Dict[str, Any]]
    career_path_response: Optional[Dict[str, Any]]
    profile_updates: Optional[Dict[str, Any]]
    content_enhancement_result: Optional[str]
    
    # Final response
    final_response: str
    profile_updated: bool
    
    # Human interaction and interrupt fields
    requires_human_input: bool  # Whether the graph needs human input
    human_input_type: Optional[str]  # Type of input needed (confirmation, clarification, etc.)
    human_input_prompt: Optional[str]  # Prompt/question for the human
    human_input_received: Optional[str]  # The actual human input received
    pending_confirmation: Optional[Dict[str, Any]]  # Data awaiting confirmation
    workflow_stage: str  # Current stage: processing, awaiting_input, confirmed, completed 