# Consolidate the WorkflowState class into a single definition in models.py
from langgraph.channels import AppendValue, add_messages

class WorkflowState(BaseModel):
    """State of the workflow."""
    task: CodingTask
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    steps: Annotated[List[ReActStep], AppendValue] = Field(default_factory=list)
    new_step: Optional[ReActStep] = None
    current_solution: Optional[str] = None
    memory_context: Annotated[List[str], AppendValue] = Field(default_factory=list)
    agent: Any = None
    error: Optional[str] = None
    model_config = {'arbitrary_types_allowed': True, 'validate_assignment': True}
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Annotated
from pydantic import BaseModel, Field
from langgraph.channels import LastValue
from langgraph.graph.message import add_messages

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class CodingTask(BaseModel):
    task_id: str = Field(..., description="Unique identifier for the task")
    description: str = Field(..., description="Description of the coding task")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    context: Dict[str, Any] = Field(default_factory=dict)
    model_config = {'frozen': True}

    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)

class CodeSolution(BaseModel):
    task_id: str = Field(..., description="Reference to the original task")
    code: str = Field(..., description="Generated code solution")
    explanation: str = Field(..., description="Explanation of the solution")
    dependencies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    model_config = {'frozen': True}

class MemoryEntry(BaseModel):
    key: str = Field(..., description="Unique identifier for the memory entry")
    content: Dict[str, Any] = Field(..., description="Content of the memory entry")
    tags: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    model_config = {'frozen': True}

    def model_dump_json(self, **kwargs):
        return super().model_dump_json(**kwargs)

class ReActStep(BaseModel):
    thought: str = Field(..., description="Agent's reasoning step")
    action: str = Field(..., description="Action to be taken")
    action_input: Dict[str, Any] = Field(..., description="Input for the action")
    observation: Optional[str] = Field(None, description="Result of the action")
    model_config = {'validate_assignment': True}

def add_step(current: List[ReActStep], new: ReActStep) -> List[ReActStep]:
    """Reducer function to add a new step to the list."""
    return current + [new] if current else [new]

class WorkflowState(BaseModel):
    """State of the workflow."""
    task: CodingTask
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    steps: Annotated[List[ReActStep], AppendValue] = Field(default_factory=list)
    new_step: Optional[ReActStep] = None
    current_solution: Optional[str] = None
    memory_context: Annotated[List[str], AppendValue] = Field(default_factory=list)
    agent: Any = None
    error: Optional[str] = None
    model_config = {'arbitrary_types_allowed': True, 'validate_assignment': True}
