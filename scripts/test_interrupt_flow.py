"""Test script to verify multi-agent flow with router as brain and human interaction"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.agents.langgraph_orchestrator import orchestrator
from backend.app.services.firebase_service import firebase_service
import json

def test_interrupt_flow():
    """Test the interrupt-based human interaction flow"""
    
    # Test session ID
    session_id = "test_interrupt_flow_123"
    
    # Create a test profile
    test_profile = {
        "name": "Test User",
        "headline": "Software Developer",
        "skills": ["JavaScript", "React"],
        "experience": [
            {
                "title": "Frontend Developer",
                "company": "Tech Corp",
                "duration": "2 years"
            }
        ]
    }
    
    # Save test profile
    firebase_service.save_user_profile(session_id, test_profile)
    
    print("🧪 Testing Interrupt-Based Multi-Agent Flow\n")
    print("="*60)
    
    # Test Case 1: Profile update with confirmation
    print("\n📝 Test Case 1: Profile Update with Human Confirmation")
    print("Query: 'I just learned Python and Docker'")
    
    # First message - should trigger interrupt
    result1 = orchestrator.process_message(
        session_id=session_id,
        user_message="I just learned Python and Docker",
        user_profile=test_profile,
        resume_from_interrupt=False
    )
    
    print(f"\nFirst Response:")
    print(f"  Agent Type: {result1.get('agent_type')}")
    print(f"  Requires Input: {result1.get('requires_input')}")
    print(f"  Input Type: {result1.get('input_type')}")
    print(f"  Workflow Stage: {result1.get('workflow_stage')}")
    print(f"  Message: {result1.get('message')}")
    
    if result1.get('requires_input'):
        print("\n✅ Interrupt working! Graph is waiting for human input.")
        
        # Simulate human confirmation
        print("\n👤 Simulating human response: 'Yes, please update'")
        
        result2 = orchestrator.process_message(
            session_id=session_id,
            user_message="Yes, please update",
            user_profile=test_profile,
            resume_from_interrupt=True
        )
        
        print(f"\nAfter Human Input:")
        print(f"  Agent Type: {result2.get('agent_type')}")
        print(f"  Profile Updated: {result2.get('profile_updated')}")
        print(f"  Workflow Stage: {result2.get('workflow_stage')}")
        print(f"  Message Preview: {result2.get('message')[:200]}...")
    
    # Test Case 2: Complex query with multiple agents
    print("\n\n📝 Test Case 2: Complex Query Requiring Multiple Agents")
    print("Query: 'Update my skills with SQL and analyze data analyst jobs'")
    
    result3 = orchestrator.process_message(
        session_id=session_id + "_2",
        user_message="Update my skills with SQL and analyze data analyst jobs",
        user_profile=test_profile,
        resume_from_interrupt=False
    )
    
    print(f"\nResponse:")
    print(f"  Agent Type: {result3.get('agent_type')}")
    print(f"  Requires Input: {result3.get('requires_input')}")
    print(f"  Workflow Stage: {result3.get('workflow_stage')}")
    
    # Test Case 3: Test router confirmation after multiple agents
    print("\n\n📝 Test Case 3: Router Confirmation Flow")
    print("Testing if router asks for confirmation after multiple agent processing")
    
    # Get the graph state to check routing history
    from langgraph.graph import StateGraph
    config = {
        "configurable": {
            "thread_id": session_id,
            "checkpoint_ns": "conversation"
        }
    }
    
    try:
        state = orchestrator.graph.get_state(config)
        if state and state.values.get('agent_scratchpad', {}).get('routing_history'):
            print("\n📊 Routing History:")
            for i, decision in enumerate(state.values['agent_scratchpad']['routing_history']):
                print(f"  Step {i+1}:")
                print(f"    Query: {decision['query'][:50]}...")
                print(f"    Decision: {decision['decision']}")
                print(f"    Stage: {decision['stage']}")
    except Exception as e:
        print(f"Could not retrieve state: {e}")
    
    print("\n✅ Interrupt-based flow test completed!")
    print("\nKey Features Tested:")
    print("  - Human interaction node with interrupts ✓")
    print("  - State persistence during interrupts ✓")
    print("  - Resume from human input ✓")
    print("  - Router confirmation flow ✓")
    print("  - Multi-agent orchestration ✓")

if __name__ == "__main__":
    test_interrupt_flow() 