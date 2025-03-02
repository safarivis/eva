from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from .models import CodingTask, CodeSolution, WorkflowState, TaskStatus
from .react_loop import ReActAgent
from .mem0_memory import Mem0Memory
import uuid
from datetime import datetime

app = FastAPI(title="Coding Agent MCP Server")
react_agent = ReActAgent()
memory = Mem0Memory()

@app.post("/tasks/", response_model=CodingTask)
async def create_task(description: str) -> CodingTask:
    """Create a new coding task."""
    task = CodingTask(
        task_id=str(uuid.uuid4()),
        description=description,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Store task in memory
    await memory.store(entry={
        "key": f"task_{task.task_id}",
        "content": task.dict(),
        "tags": ["task"]
    })
    
    return task

@app.get("/tasks/{task_id}", response_model=CodingTask)
async def get_task(task_id: str) -> CodingTask:
    """Get a specific task by ID."""
    memories = await memory.retrieve(f"task_{task_id}")
    if not memories:
        raise HTTPException(status_code=404, detail="Task not found")
    return CodingTask(**memories[0].content)

@app.post("/tasks/{task_id}/solve", response_model=WorkflowState)
async def solve_task(task_id: str) -> WorkflowState:
    """Solve a coding task using the ReAct agent."""
    # Get the task
    task_memories = await memory.retrieve(f"task_{task_id}")
    if not task_memories:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = CodingTask(**task_memories[0].content)
    
    # Create initial workflow state
    workflow_state = WorkflowState(task=task)
    
    # Solve the task
    workflow_state = await react_agent.solve_task(workflow_state)
    
    # Store the solution if task was completed
    if workflow_state.task.status == TaskStatus.COMPLETED and workflow_state.current_solution:
        await memory.store(entry={
            "key": f"solution_{task_id}",
            "content": workflow_state.current_solution.dict(),
            "tags": ["solution"]
        })
    
    return workflow_state

@app.get("/solutions/{task_id}", response_model=CodeSolution)
async def get_solution(task_id: str) -> CodeSolution:
    """Get the solution for a specific task."""
    memories = await memory.retrieve(f"solution_{task_id}")
    if not memories:
        raise HTTPException(status_code=404, detail="Solution not found")
    return CodeSolution(**memories[0].content)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
