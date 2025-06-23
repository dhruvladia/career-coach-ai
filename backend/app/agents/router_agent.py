from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
<<<<<<< HEAD
import json
=======
>>>>>>> fa29382d12c4f71e87bff507946ee59378543435

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
<<<<<<< HEAD
            ("system", """You are the brain of a career coaching AI system. You orchestrate the flow between specialized agents to provide comprehensive assistance.

Available agents:
- profile_updater: Updates user profile with new skills, experience, or background information
- job_fit_analyst: Analyzes job descriptions and evaluates job fit
- content_enhancement: Improves LinkedIn profile content and professional materials
- career_path: Provides career guidance, trajectory planning, and general advice

Your responsibilities:
1. Analyze the user's query to determine which agent(s) need to be involved
2. Consider if multiple agents should be engaged for comprehensive responses
3. Track which agents have already been used to avoid redundancy
4. Decide when the query has been fully addressed

Complex query examples that might need multiple agents:
- "I just learned Python and want to know what jobs I qualify for" → profile_updater THEN job_fit_analyst
- "Update my skills and suggest how to improve my LinkedIn" → profile_updater THEN content_enhancement
- "I want to transition to data science, what should I do?" → career_path (might suggest profile_updater after)

Response format:
Respond with a JSON object containing:
- "agent": The next agent to route to (or "end" if done)
- "reasoning": Brief explanation of your decision
- "needs_followup": true/false - whether another agent might be needed after this one

Example: {{"agent": "profile_updater", "reasoning": "User provided new skill information", "needs_followup": true}}"""),
=======
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
>>>>>>> fa29382d12c4f71e87bff507946ee59378543435
            ("human", """Current user query: {user_query}

Chat history context: {chat_history}

<<<<<<< HEAD
Routing context: {routing_context}

Which agent should handle this next?""")
=======
Which agent should handle this query?""")
>>>>>>> fa29382d12c4f71e87bff507946ee59378543435
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def route_query(self, state: GraphState) -> GraphState:
        """Route the user query to the appropriate agent"""
        
        # Get recent chat history for context
        recent_history = []
        if state.get("chat_history"):
            recent_history = state["chat_history"][-4:]  # Last 4 messages
        
<<<<<<< HEAD
        # Get routing context (which agents have already been used)
        routing_context = state.get("agent_scratchpad", {}).get("routing_context", "First routing - no agents used yet")
        
        try:
            # Get routing decision
            response = self.chain.invoke({
                "user_query": state["current_user_query"],
                "chat_history": "\n".join([f"{msg.type}: {msg.content}" for msg in recent_history]),
                "routing_context": routing_context
            })
            
            # Parse JSON response
            decision_data = json.loads(response)
            agent_decision = decision_data.get("agent", "career_path").strip().lower()
            needs_followup = decision_data.get("needs_followup", False)
            
        except Exception as e:
            # Fallback to simple parsing if JSON fails
            print(f"Router parsing error: {e}")
            agent_decision = "career_path"
            needs_followup = False
        
        # Validate the decision
        valid_agents = ["profile_updater", "job_fit_analyst", "content_enhancement", "career_path", "end"]
        if agent_decision not in valid_agents:
            agent_decision = "career_path"  # Default fallback
        
        # Update state
        state["router_decision"] = agent_decision
        state["agent_type"] = agent_decision if agent_decision != "end" else state.get("agent_type", "router")
        
        # Set next_agent based on whether followup is needed
        if needs_followup and agent_decision != "end":
            state["next_agent"] = "router"  # Come back to router after this agent
        else:
            state["next_agent"] = "end"  # Go to response compiler after this agent
        
        # Store routing decision in scratchpad for debugging
        if "routing_decisions" not in state.get("agent_scratchpad", {}):
            state["agent_scratchpad"]["routing_decisions"] = []
        state["agent_scratchpad"]["routing_decisions"].append({
            "query": state["current_user_query"],
            "decision": agent_decision,
            "needs_followup": needs_followup
        })
=======
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
>>>>>>> fa29382d12c4f71e87bff507946ee59378543435
        
        return state

# Create agent instance
router_agent = RouterAgent() 