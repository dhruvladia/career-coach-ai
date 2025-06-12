from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, List
import json

from app.agents.state import GraphState
from app.agents.router_agent import router_agent
from app.agents.job_fit_analyst import job_fit_analyst
from app.agents.career_path_agent import career_path_agent
from app.agents.profile_updater import profile_updater
from app.agents.content_enhancement_agent import content_enhancement_agent
from app.services.firebase_service import firebase_service

class LangGraphOrchestrator:
    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(GraphState)
        
        # Add nodes (agents)
        workflow.add_node("router", self._router_node)
        workflow.add_node("profile_updater", self._profile_updater_node)
        workflow.add_node("job_fit_analyst", self._job_fit_analyst_node)
        workflow.add_node("career_path", self._career_path_node)
        workflow.add_node("content_enhancement", self._content_enhancement_node)
        
        # Add edges
        workflow.set_entry_point("router")
        
        # Router decides which agent to use
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "profile_updater": "profile_updater",
                "job_fit_analyst": "job_fit_analyst",
                "career_path": "career_path",
                "content_enhancement": "content_enhancement"
            }
        )
        
        # All agents end after processing
        workflow.add_edge("profile_updater", END)
        workflow.add_edge("job_fit_analyst", END)
        workflow.add_edge("career_path", END)
        workflow.add_edge("content_enhancement", END)
        
        # Compile the graph
        return workflow.compile(checkpointer=self.memory)
    
    def _router_node(self, state: GraphState) -> GraphState:
        """Router agent node"""
        return router_agent.route_query(state)
    
    def _profile_updater_node(self, state: GraphState) -> GraphState:
        """Profile updater agent node"""
        return profile_updater.update_profile(state)
    
    def _job_fit_analyst_node(self, state: GraphState) -> GraphState:
        """Job fit analyst agent node"""
        return job_fit_analyst.analyze_job_fit(state)
    
    def _career_path_node(self, state: GraphState) -> GraphState:
        """Career path agent node"""
        return career_path_agent.provide_career_guidance(state)
    
    def _content_enhancement_node(self, state: GraphState) -> GraphState:
        """Content enhancement agent node"""
        return content_enhancement_agent.enhance_content(state)
    
    def _route_decision(self, state: GraphState) -> str:
        """Decide which agent to route to based on router decision"""
        return state.get("router_decision", "career_path")
    
    def process_message(self, session_id: str, user_message: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user message through the multi-agent system"""
        
        try:
            # Get existing conversation state or create new
            conversation_state = firebase_service.get_conversation_state(session_id)
            
            # Get chat history
            chat_history = firebase_service.get_chat_history(session_id, limit=6)
            
            # Convert chat history to LangChain messages
            messages = []
            for chat in reversed(chat_history):  # Reverse to get chronological order
                messages.append(HumanMessage(content=chat.get("message", "")))
                messages.append(AIMessage(content=chat.get("response", "")))
            
            # Add current message
            messages.append(HumanMessage(content=user_message))
            
            # Create initial state
            initial_state = {
                "session_id": session_id,
                "user_profile_data": user_profile,
                "current_user_query": user_message,
                "chat_history": messages,
                "agent_type": "",
                "next_agent": None,
                "agent_scratchpad": {},
                "router_decision": "",
                "job_fit_analysis": None,
                "career_path_response": None,
                "profile_updates": None,
                "content_enhancement_result": None,
                "final_response": "",
                "profile_updated": False
            }
            
            # Create thread configuration
            config = {
                "configurable": {
                    "thread_id": session_id,
                    "checkpoint_ns": "conversation"
                }
            }
            
            # Process through the graph
            result = self.graph.invoke(initial_state, config=config)
            
            # Save conversation state
            self._save_conversation_state(session_id, result)
            
            # Save chat history
            firebase_service.add_chat_history(
                session_id=session_id,
                message=user_message,
                response=result.get("final_response", ""),
                agent_type=result.get("agent_type", "unknown")
            )
            
            # Return structured response
            return {
                "message": result.get("final_response", "I'm sorry, I couldn't process your request."),
                "agent_type": result.get("agent_type", "unknown"),
                "session_id": session_id,
                "profile_updated": result.get("profile_updated", False),
                "job_fit_analysis": result.get("job_fit_analysis"),
                "career_path": result.get("career_path_response"),
                "profile_updates": result.get("profile_updates")
            }
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "message": "I encountered an error processing your request. Please try again.",
                "agent_type": "error",
                "session_id": session_id,
                "profile_updated": False,
                "job_fit_analysis": None,
                "career_path": None,
                "profile_updates": None
            }
    
    def _save_conversation_state(self, session_id: str, state: Dict[str, Any]):
        """Save the conversation state to Firestore"""
        try:
            # Clean state for storage (remove non-serializable items)
            clean_state = {}
            for key, value in state.items():
                if key == "chat_history":
                    # Convert messages to serializable format
                    clean_state[key] = [
                        {"type": msg.type, "content": msg.content} 
                        for msg in value if hasattr(msg, 'type') and hasattr(msg, 'content')
                    ]
                elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    clean_state[key] = value
            
            firebase_service.save_conversation_state(session_id, clean_state)
            
        except Exception as e:
            print(f"Error saving conversation state: {e}")

# Create the orchestrator instance
orchestrator = LangGraphOrchestrator() 