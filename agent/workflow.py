# In workflow.py, update the execute_step function:
async def execute_step(state: WorkflowState) -> Dict[str, Any]:
    """Execute the current step and update the workflow state."""
    if state.new_step is None:
        return {"next": "should_continue", "state": state}

    try:
        # Execute the step with both parameters
        observation = await state.agent.execute_step(state.new_step, state)
        
        # Rest of the function remains the same
        # ...
from typing import Dict, Any, List, Optional, Union, Literal, Annotated, ForwardRef
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
import asyncio
from operator import add

# Import models first
from agent.models import CodingTask, ReActStep, TaskStatus

class WorkflowState(BaseModel):
    """State of the workflow."""
    task: CodingTask
    steps: Annotated[List[ReActStep], add] = Field(default_factory=list)
    new_step: Optional[ReActStep] = None
    current_solution: Optional[str] = None
    memory_context: Annotated[List[str], add] = Field(default_factory=list)
    agent: Any
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

# Define state update functions
def append_steps(current: List["ReActStep"], update: List["ReActStep"]) -> List["ReActStep"]:
    """Append new steps to the current list."""
    if not update:
        return current
    return current + update

def update_memory_context(current: List[str], update: List[str]) -> List[str]:
    """Update memory context by appending new entries."""
    if not update:
        return current
    return current + update

def validate_state(state: WorkflowState) -> Optional[str]:
    """Validate the workflow state."""
    if state.task is None:
        return "Missing task in state"
    if state.agent is None:
        return "Missing agent in state"
    return None

def calculate_backoff(retry_count: int, base_delay: int = 1000) -> int:
    """Calculate exponential backoff delay in milliseconds."""
    return min(base_delay * (2 ** retry_count), 30000)  # Max 30 seconds

async def generate_step(state: WorkflowState) -> Dict[str, Any]:
    """Generate the next step in the workflow."""
    try:
        # Get the next step from the agent
        next_step = await state.agent._get_next_step(state)
        
        # Return state update
        return {
            "next": "execute_step",
            "state": state.model_copy(update={"new_step": next_step})
        }
    except Exception as e:
        return {
            "next": "handle_error",
            "state": state.model_copy(update={"error": str(e)})
        }

async def execute_step(state: WorkflowState) -> Dict[str, Any]:
    """Execute the current step and update the workflow state."""
    if state.new_step is None:
        return {"next": "should_continue", "state": state}

    try:
        # Execute the step
        observation = await state.agent.execute_step(state.new_step)
        
        # Create executed step with observation
        executed_step = state.new_step.model_copy()
        executed_step.observation = observation
        
        # Create new state with updates
        new_state = state.model_copy()
        new_state.steps.append(executed_step)
        new_state.new_step = None
        
        # Update task status if it's a finish action
        if executed_step.action == "finish":
            new_state.task.status = TaskStatus.COMPLETED
            
        return {
            "next": "should_continue",
            "state": new_state
        }
    except Exception as e:
        return {
            "next": "handle_error",
            "state": state.model_copy(update={"error": str(e)})
        }

async def should_continue(state: WorkflowState) -> Dict[str, Any]:
    """Determine if the workflow should continue or end."""
    # End if there's an error
    if state.error is not None:
        return {"next": "handle_error", "state": state}
    
    # End if the task is completed
    if state.task.status == TaskStatus.COMPLETED:
        return {"next": "end", "state": state}
        
    # End if the last step was a finish action
    if state.steps and state.steps[-1].action == "finish":
        new_state = state.model_copy()
        new_state.task.status = TaskStatus.COMPLETED
        return {"next": "end", "state": new_state}
    
    return {"next": "generate_step", "state": state}

async def handle_error(state: WorkflowState) -> Dict[str, Any]:
    """Handle errors in the workflow with human intervention and exponential backoff."""
    if state.error is None:
        return {"next": "should_continue", "state": state}

    # Get retry count from context
    retry_count = state.task.context.get("retry_count", 0)
    
    # For critical errors or after max retries, ask for human intervention
    if retry_count >= 3 or "State validation failed" in state.error:
        try:
            # Request human assistance
            human_response = await interrupt({
                "error": state.error,
                "state": state.model_dump(),
                "question": "How should we proceed? (retry/fail/continue)"
            })

            action = human_response.get("action", "fail").lower()
            if action == "retry":
                # Reset retry count
                new_task = state.task.model_copy(update={
                    "context": {"retry_count": 0}
                })
                new_state = state.model_copy(update={
                    "task": new_task,
                    "error": None
                })
                return {
                    "next": "should_continue",
                    "state": new_state
                }
            elif action == "continue":
                new_state = state.model_copy(update={"error": None})
                return {
                    "next": "should_continue",
                    "state": new_state
                }
            else:  # fail
                new_task = state.task.model_copy(update={
                    "status": TaskStatus.FAILED,
                    "context": {"error": state.error}
                })
                new_state = state.model_copy(update={"task": new_task})
                return {
                    "next": "end",
                    "state": new_state
                }
        except Exception as e:
            # If human intervention fails, mark as failed
            new_task = state.task.model_copy(update={
                "status": TaskStatus.FAILED,
                "context": {"error": f"Human intervention failed: {str(e)}"}
            })
            new_state = state.model_copy(update={"task": new_task})
            return {
                "next": "end",
                "state": new_state
            }

    # Calculate backoff delay
    delay = calculate_backoff(retry_count)
    
    # Update retry count
    new_state = state.model_copy()
    new_state.task.context["retry_count"] = retry_count + 1
    new_state.error = None  # Clear the error
    
    # Sleep for the backoff delay
    await asyncio.sleep(delay / 1000)  # Convert to seconds
    
    return {"next": "should_continue", "state": new_state}

def create_workflow_graph() -> StateGraph:
    """Create the workflow graph."""
    # Initialize graph with state type
    workflow = StateGraph(WorkflowState)

    # Add nodes for step generation and execution
    workflow.add_node("generate_step", generate_step)
    workflow.add_node("execute_step", execute_step)
    workflow.add_node("should_continue", should_continue)
    workflow.add_node("handle_error", handle_error)

    # Add edges for the sequential flow
    workflow.add_edge("generate_step", "execute_step")
    workflow.add_edge("execute_step", "should_continue")
    
    # Add conditional edges for should_continue
    workflow.add_conditional_edges(
        "should_continue",
        lambda x: x["next"] if isinstance(x, dict) and "next" in x else "end",
        {
            "generate_step": "generate_step",
            "handle_error": "handle_error",
            "end": END
        }
    )

    # Add conditional edges for handle_error
    workflow.add_conditional_edges(
        "handle_error",
        lambda x: x["next"] if isinstance(x, dict) and "next" in x else "end",
        {
            "should_continue": "should_continue",
            "end": END
        }
    )

    # Set the entry point
    workflow.set_entry_point("generate_step")

    # Compile with config
    compiled = workflow.compile()
    compiled.config = {"recursion_limit": 100}
    return compiled

def create_workflow_agent(agent: Any) -> StateGraph:
    """Create a workflow agent with the given agent."""
    graph = create_workflow_graph()
    return graph
