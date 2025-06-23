from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, List, Optional # Keep Optional
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
        """Build the LangGraph workflow with proper interrupt handling""" # Keep this docstring

        # Create the graph
        workflow = StateGraph(GraphState)

        # Add nodes (agents) - Keep all nodes from HEAD
        workflow.add_node("router", self._router_node)
        workflow.add_node("profile_updater", self._profile_updater_node)
        workflow.add_node("job_fit_analyst", self._job_fit_analyst_node)
        workflow.add_node("career_path", self._career_path_node)
        workflow.add_node("content_enhancement", self._content_enhancement_node)
        workflow.add_node("human_interaction", self._human_interaction_node)
        workflow.add_node("resume_after_human", self._resume_after_human_node)
        workflow.add_node("router_confirmation", self._router_confirmation_node)
        workflow.add_node("finalize_response", self._finalize_response_node)

        # Set entry point - always start with router
        workflow.set_entry_point("router")

        # Router routes to agents or human interaction
        workflow.add_conditional_edges(
            "router",
            self._route_from_router, # Keep this route function
            {
                "profile_updater": "profile_updater",
                "job_fit_analyst": "job_fit_analyst",
                "career_path": "career_path",
                "content_enhancement": "content_enhancement",
                "human_interaction": "human_interaction",
                "finalize": "finalize_response"
            }
        )

        # All agents go to router_confirmation
        for agent in ["profile_updater", "job_fit_analyst", "career_path", "content_enhancement"]:
            workflow.add_edge(agent, "router_confirmation")

        # Router confirmation decides next step
        workflow.add_conditional_edges(
            "router_confirmation",
            self._route_from_confirmation,
            {
                "router": "router",
                "human_interaction": "human_interaction",
                "finalize": "finalize_response"
            }
        )

        # Human interaction interrupts and waits
        workflow.add_conditional_edges(
            "human_interaction",
            self._check_human_input,
            {
                "wait": "human_interaction",  # Loop waiting for input
                "resume": "resume_after_human"
            }
        )

        # Resume after human input goes back to router
        workflow.add_edge("resume_after_human", "router")

        # Finalize always ends
        workflow.add_edge("finalize_response", END)

        # Compile with interrupt support
        return workflow.compile(
            checkpointer=self.memory,
            interrupt_before=["human_interaction"]  # Interrupt before human node
        )

    def _router_node(self, state: GraphState) -> GraphState:
        """Router agent node - orchestrates the flow"""
        # Check if we're resuming from human input
        if state.get("human_input_received"):
            state["current_user_query"] = state["human_input_received"]
            state["human_input_received"] = None

        # Track routing context
        if "routing_history" not in state.get("agent_scratchpad", {}):
            state["agent_scratchpad"]["routing_history"] = []

        # Route the query
        result = router_agent.route_query(state)

        # Record this routing decision
        state["agent_scratchpad"]["routing_history"].append({
            "query": state["current_user_query"],
            "decision": result["router_decision"],
            "stage": state.get("workflow_stage", "processing")
        })

        return result

    def _router_confirmation_node(self, state: GraphState) -> GraphState:
        """Router confirmation - decides if we need more processing or human input"""
        # Check if any agent flagged need for human confirmation
        if state.get("pending_confirmation"):
            state["requires_human_input"] = True
            state["human_input_type"] = "confirmation"
            state["workflow_stage"] = "awaiting_confirmation"
            return state

        # Check if we've processed enough agents
        completed_agents = state.get("agent_scratchpad", {}).get("completed_agents", [])
        if len(completed_agents) >= 2:  # If multiple agents used, might need confirmation
            state["requires_human_input"] = True
            state["human_input_type"] = "review"
            state["human_input_prompt"] = "I've analyzed your request from multiple angles. Would you like me to continue or is this sufficient?"
            state["workflow_stage"] = "awaiting_input"
            return state

        # Otherwise, continue processing or finalize
        state["workflow_stage"] = "confirmed"
        return state

    def _human_interaction_node(self, state: GraphState) -> GraphState:
        """Human interaction node - prepares for human input and waits"""
        # This node will be interrupted, allowing the graph to pause
        # The state is automatically persisted by LangGraph

        if not state.get("human_input_prompt"):
            # Generate appropriate prompt based on context
            if state.get("human_input_type") == "confirmation":
                if state.get("pending_confirmation"):
                    conf_data = state["pending_confirmation"]
                    state["human_input_prompt"] = conf_data.get("prompt", "Please confirm this action.")
            elif state.get("human_input_type") == "clarification":
                state["human_input_prompt"] = "I need more information to proceed. Could you clarify your request?"
            else:
                state["human_input_prompt"] = "How would you like me to proceed?"

        state["workflow_stage"] = "awaiting_input"
        return state

    def _resume_after_human_node(self, state: GraphState) -> GraphState:
        """Resume node - processes human input and continues workflow"""
        human_input = state.get("human_input_received", "")

        # Process the human input based on type
        if state.get("human_input_type") == "confirmation":
            if human_input.lower() in ["yes", "confirm", "proceed", "y"]:
                state["workflow_stage"] = "confirmed"
                # Apply any pending changes
                if state.get("pending_confirmation", {}).get("action") == "profile_update":
                    state["profile_updated"] = True
            else:
                state["workflow_stage"] = "cancelled"
                state["final_response"] = "Understood. I've cancelled that action. How else can I help you?"

        # Clear human interaction fields
        state["requires_human_input"] = False
        state["human_input_type"] = None
        state["human_input_prompt"] = None
        state["pending_confirmation"] = None

        return state

    def _finalize_response_node(self, state: GraphState) -> GraphState:
        """Compile all agent outputs into final response"""
        responses = []

        # Gather all agent outputs
        if state.get("profile_updates"):
            profile_data = state["profile_updates"]
            if isinstance(profile_data, dict) and profile_data.get("message"):
                responses.append(profile_data["message"])

        if state.get("job_fit_analysis"):
            analysis = state["job_fit_analysis"]
            if isinstance(analysis, dict) and analysis.get("analysis"):
                responses.append(analysis["analysis"])

        if state.get("career_path_response"):
            career_resp = state["career_path_response"]
            if isinstance(career_resp, dict) and career_resp.get("guidance"):
                responses.append(career_resp["guidance"])
            elif isinstance(career_resp, str):
                responses.append(career_resp)

        if state.get("content_enhancement_result"):
            responses.append(state["content_enhancement_result"])

        # Compile final response
        if responses:
            state["final_response"] = "\n\n".join(responses)
        elif not state.get("final_response"):
            state["final_response"] = "I've completed processing your request. How else can I help you?"

        state["workflow_stage"] = "completed"
        return state

    def _route_from_router(self, state: GraphState) -> str:
        """Routing logic from router node"""
        decision = state.get("router_decision", "")

        # Check if we need human input first
        if state.get("requires_human_input"):
            return "human_interaction"

        # Check if router decided to end
        if decision == "end" or state.get("workflow_stage") == "cancelled":
            return "finalize"

        # Route to appropriate agent
        if decision in ["profile_updater", "job_fit_analyst", "career_path", "content_enhancement"]:
            return decision

        return "finalize"

    def _route_from_confirmation(self, state: GraphState) -> str:
        """Routing logic from router confirmation"""
        if state.get("requires_human_input"):
            return "human_interaction"

        # Check if we need more processing
        if state.get("next_agent") == "router":
            return "router"

        return "finalize"

    def _check_human_input(self, state: GraphState) -> str:
        """Check if human input has been received"""
        if state.get("human_input_received"):
            return "resume"
        return "wait"  # Keep waiting

    def _profile_updater_node(self, state: GraphState) -> GraphState:
        """Profile updater with confirmation requirement"""
        result = profile_updater.update_profile(state)

        # If profile would be updated, require confirmation
        if result.get("profile_updates") and not result.get("profile_updated"):
            state["pending_confirmation"] = {
                "action": "profile_update",
                "updates": result["profile_updates"],
                "prompt": f"I found new information to add to your profile. Should I update it with: {result['profile_updates'].get('message', 'these changes')}?"
            }
            state["requires_human_input"] = True

        # Track completion
        if "completed_agents" not in state.get("agent_scratchpad", {}):
            state["agent_scratchpad"]["completed_agents"] = []
        state["agent_scratchpad"]["completed_agents"].append("profile_updater")

        return state

    def _job_fit_analyst_node(self, state: GraphState) -> GraphState:
        """Job fit analyst agent node"""
        result = job_fit_analyst.analyze_job_fit(state)

        # Track completion
        if "completed_agents" not in state.get("agent_scratchpad", {}):
            state["agent_scratchpad"]["completed_agents"] = []
        state["agent_scratchpad"]["completed_agents"].append("job_fit_analyst")

        return result

    def _career_path_node(self, state: GraphState) -> GraphState:
        """Career path agent node"""
        result = career_path_agent.provide_career_guidance(state)

        # Track completion
        if "completed_agents" not in state.get("agent_scratchpad", {}):
            state["agent_scratchpad"]["completed_agents"] = []
        state["agent_scratchpad"]["completed_agents"].append("career_path")

        return result

    def _content_enhancement_node(self, state: GraphState) -> GraphState:
        """Content enhancement agent node"""
        result = content_enhancement_agent.enhance_content(state)

        # Track completion
        if "completed_agents" not in state.get("agent_scratchpad", {}):
            state["agent_scratchpad"]["completed_agents"] = []
        state["agent_scratchpad"]["completed_agents"].append("content_enhancement")

        return result

    def process_message(self, session_id: str, user_message: str,
                        user_profile: Dict[str, Any],
                        resume_from_interrupt: bool = False) -> Dict[str, Any]:
        """Process a message through the graph with interrupt handling"""

        try:
            # Get thread configuration
            config = {
                "configurable": {
                    "thread_id": session_id,
                }
            }

            if resume_from_interrupt:
                # Resume from interrupted state
                # Get the current state from checkpoint
                current_state = self.graph.get_state(config)
                if current_state and current_state.values.get("requires_human_input"):
                    # Add human input to state
                    current_state.values["human_input_received"] = user_message

                    # Update the state
                    self.graph.update_state(config, current_state.values)

                    # Continue execution from where it was interrupted
                    result = None
                    for event in self.graph.stream(None, config=config):
                        result = event
                else:
                    # No interrupt state found, treat as new message
                    resume_from_interrupt = False

            if not resume_from_interrupt:
                # New message - create initial state
                chat_history = firebase_service.get_chat_history(session_id, limit=6)
                messages = []
                for chat in reversed(chat_history):
                    messages.append(HumanMessage(content=chat.get("message", "")))
                    messages.append(AIMessage(content=chat.get("response", "")))
                messages.append(HumanMessage(content=user_message))

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
                    "profile_updated": False,
                    "requires_human_input": False,
                    "human_input_type": None,
                    "human_input_prompt": None,
                    "human_input_received": None,
                    "pending_confirmation": None,
                    "workflow_stage": "processing"
                }

                # Process through graph
                result = None
                for event in self.graph.stream(initial_state, config=config):
                    result = event

            # Get final state
            final_state = self.graph.get_state(config).values

            # Check if we're interrupted and waiting for human input
            if final_state.get("requires_human_input"):
                return {
                    "message": final_state.get("human_input_prompt", "Please provide input to continue."),
                    "agent_type": "human_interaction",
                    "session_id": session_id,
                    "requires_input": True,
                    "input_type": final_state.get("human_input_type", "general"),
                    "workflow_stage": "awaiting_input"
                }

            # Save conversation if completed
            if final_state.get("workflow_stage") == "completed":
                firebase_service.add_chat_history(
                    session_id=session_id,
                    message=user_message,
                    response=final_state.get("final_response", ""),
                    agent_type=final_state.get("agent_type", "unknown")
                )

            return {
                "message": final_state.get("final_response", "Processing complete."),
                "agent_type": final_state.get("agent_type", "unknown"),
                "session_id": session_id,
                "profile_updated": final_state.get("profile_updated", False),
                "job_fit_analysis": final_state.get("job_fit_analysis"),
                "career_path": final_state.get("career_path_response"),
                "profile_updates": final_state.get("profile_updates"),
                "workflow_stage": final_state.get("workflow_stage", "completed")
            }

        except Exception as e:
            print(f"Error in process_message: {e}")
            import traceback
            traceback.print_exc()
            return {
                "message": "I encountered an error processing your request. Please try again.",
                "agent_type": "error",
                "session_id": session_id,
                "workflow_stage": "error"
            }

# Create the orchestrator instance
orchestrator = LangGraphOrchestrator()
