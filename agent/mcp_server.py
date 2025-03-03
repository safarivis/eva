from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
from agent.models import CodingTask, CodeSolution, WorkflowState, TaskStatus
from agent.mem0_memory import Mem0Memory
from agent.react_loop import ReActAgent
import uuid
from datetime import datetime, timezone
import pytz
import os
import openai

class MCPServer:
    def __init__(self, agent: ReActAgent, memory: Mem0Memory):
        self.app = FastAPI(title="Coding Agent MCP Server")
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.agent = agent
        self.memory = memory
        self.setup_routes()
    
    def setup_routes(self):
        """Set up FastAPI routes."""
        self.app.post("/tasks/")(self.create_task)
        self.app.get("/tasks/{task_id}")(self.get_task)
        self.app.post("/tasks/{task_id}/solve")(self.solve_task)
        self.app.get("/solutions/{task_id}")(self.get_solution)
        self.app.get("/health")(self.health_check)
    
    async def create_task(self, description: str) -> CodingTask:
        """Create a new coding task."""
        task = CodingTask(
            task_id=f"task_{datetime.now(timezone.utc).timestamp()}",
            description=description,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            context={},
            model_config={'frozen': False}
        )
        
        # Store task in memory
        await self.memory.store_task(task)
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[CodingTask]:
        """Get a specific task by ID."""
        return await self.memory.get_task(task_id)
    
    async def solve_task(self, task_id: str) -> Optional[CodingTask]:
        """Solve a coding task using the React agent."""
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # Create initial workflow state
        workflow_state = WorkflowState(
            task=task,
            steps=[],
            current_solution=None,
            memory_context=[],
            agent=self.agent
        )
        
        # Solve task using React agent
        result = await self.agent.solve_task(workflow_state)
        return result.task
    
    async def get_solution(self, task_id: str) -> CodeSolution:
        """Get the solution for a specific task."""
        memories = await self.memory.retrieve(f"solution_{task_id}")
        if not memories:
            raise HTTPException(status_code=404, detail="Solution not found")
        return CodeSolution(**memories[0].content)
    
    async def health_check(self) -> Dict[str, str]:
        """Check if the server is healthy."""
        return {"status": "ok"}
