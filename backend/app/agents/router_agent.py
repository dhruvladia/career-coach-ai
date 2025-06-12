from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any

from app.config import settings
from app.agents.state import GraphState

class RouterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o-mini",
            temperature=0.1
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a routing agent for a career coaching AI system. Your job is to analyze user queries and route them to the appropriate specialized agent.

Available agents:
- profile_updater: When user provides new information about their skills, experience, or background
- job_fit_analyst: When user wants to analyze a job description or check job fit
- content_enhancement: When user wants help improving their LinkedIn profile content
- career_path: When user asks for career guidance, trajectory planning, or general advice

Rules:
1. Look for keywords and context clues in the user's message
2. Consider the chat history if relevant
3. Choose the MOST appropriate single agent
4. If unclear, default to 'career_path' for general career questions

Respond with ONLY the agent name (one of: profile_updater, job_fit_analyst, content_enhancement, career_path)"""),
            ("human", """Current user query: {user_query}

Chat history context: {chat_history}

Which agent should handle this query?""")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def route_query(self, state: GraphState) -> GraphState:
        """Route the user query to the appropriate agent"""
        
        # Get recent chat history for context
        recent_history = []
        if state.get("chat_history"):
            recent_history = state["chat_history"][-4:]  # Last 4 messages
        
        # Route the query
        decision = self.chain.invoke({
            "user_query": state["current_user_query"],
            "chat_history": "\n".join([f"{msg.type}: {msg.content}" for msg in recent_history])
        })
        
        # Clean up the decision (remove any extra whitespace/formatting)
        decision = decision.strip().lower()
        
        # Validate the decision
        valid_agents = ["profile_updater", "job_fit_analyst", "content_enhancement", "career_path"]
        if decision not in valid_agents:
            decision = "career_path"  # Default fallback
        
        # Update state
        state["router_decision"] = decision
        state["agent_type"] = decision
        state["next_agent"] = decision
        
        return state

# Create agent instance
router_agent = RouterAgent() 