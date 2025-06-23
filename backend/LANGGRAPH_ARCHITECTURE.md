# LangGraph Multi-Agent Architecture

## Overview

This implementation follows the proper LangGraph patterns with:
- **Router as the brain** orchestrating the entire flow
- **Human interaction nodes** with interrupt capability
- **State persistence** during interrupts
- **Router confirmation** after agent processing

## Architecture Flow

```
Router Node → Child Agent Nodes → Router Confirmation → Human Node (if needed) → User
```

## Key Components

### 1. Router Agent (Brain)
The router is the central orchestrator that:
- Analyzes user queries and determines which agents to invoke
- Tracks routing history and completed agents
- Supports complex multi-agent workflows
- Returns JSON with routing decisions and follow-up requirements

### 2. Agent Nodes
Specialized agents that process specific tasks:
- **Profile Updater**: Updates user profile with confirmation
- **Job Fit Analyst**: Analyzes job descriptions
- **Career Path**: Provides career guidance
- **Content Enhancement**: Improves LinkedIn content

### 3. Router Confirmation Node
Reviews agent outputs and decides:
- Whether to continue processing (back to router)
- Request human confirmation (to human interaction node)
- Finalize the response

### 4. Human Interaction Node (Interrupt)
Implements proper interrupt pattern:
- Graph state is frozen when human input is needed
- State persists in LangGraph checkpointer
- Resume node processes human input and continues workflow
- No graph killing - maintains consistency and memory

### 5. Finalize Response Node
Compiles all agent outputs into a cohesive final response.

## State Management

The `GraphState` includes:
```python
# Human interaction fields
requires_human_input: bool
human_input_type: Optional[str]  # confirmation, clarification, etc.
human_input_prompt: Optional[str]
human_input_received: Optional[str]
pending_confirmation: Optional[Dict[str, Any]]
workflow_stage: str  # processing, awaiting_input, confirmed, completed
```

## Interrupt Flow Example

1. User: "I just learned Python"
2. Router → Profile Updater
3. Profile Updater detects new skill, sets pending_confirmation
4. Router Confirmation → Human Interaction Node
5. **INTERRUPT** - Graph pauses, state persisted
6. System: "Should I update your profile with Python?"
7. User: "Yes"
8. Resume node processes confirmation
9. Router continues flow or finalizes response

## API Integration

The `/chat` endpoint supports:
- `resume_from_interrupt`: Boolean flag to resume interrupted flow
- Returns `requires_input` when waiting for human interaction
- Maintains session state across interrupts

## Benefits

1. **Proper State Management**: No graph killing, maintains consistency
2. **True Interrupt Capability**: Graph freezes and resumes properly
3. **Complex Workflows**: Supports multi-agent orchestration
4. **Human in the Loop**: Natural confirmation and clarification flows
5. **Scalable Architecture**: Easy to add new agents or interaction types

## Testing

Run the interrupt flow test:
```bash
python scripts/test_interrupt_flow.py
```

This tests:
- Human interaction interrupts
- State persistence during interrupts
- Resume from human input
- Router confirmation flow
- Multi-agent orchestration 