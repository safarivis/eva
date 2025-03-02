from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class CodingTask(BaseModel):
    model_config = ConfigDict(frozen=True)  # Immutable model
    
    task_id: str = Field(..., description="Unique identifier for the task")
    description: str = Field(..., description="Description of the coding task")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    context: Dict[str, Any] = Field(default_factory=dict)
    
    def model_dump(self, **kwargs):
        # Customize serialization if needed
        return super().model_dump(**kwargs)

class CodeSolution(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    task_id: str = Field(..., description="Reference to the original task")
    code: str = Field(..., description="Generated code solution")
    explanation: str = Field(..., description="Explanation of the solution")
    dependencies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

class MemoryEntry(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    key: str = Field(..., description="Unique identifier for the memory entry")
    content: Dict[str, Any] = Field(..., description="Content of the memory entry")
    tags: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def model_dump_json(self, **kwargs):
        # Customize JSON serialization if needed
        return super().model_dump_json(**kwargs)
    
class ReActStep(BaseModel):
    model_config = ConfigDict(validate_assignment=True)  # Validate on assignment
    
    thought: str = Field(..., description="Agent's reasoning step")
    action: Optional[str] = Field(None, description="Action to be taken")
    action_input: Optional[Dict[str, Any]] = Field(None, description="Input for the action")
    observation: Optional[str] = Field(None, description="Result of the action")
    
class WorkflowState(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    task: CodingTask
    steps: List[ReActStep] = Field(default_factory=list)
    current_solution: Optional[CodeSolution] = None
    memory_context: List[MemoryEntry] = Field(default_factory=list)
