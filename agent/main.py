import typer
import uvicorn
from typing import Optional
import asyncio
from .mcp_server import app
from .models import CodingTask, TaskStatus
from .react_loop import ReActAgent
from .mem0_memory import Mem0Memory
import uuid
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()
cli = typer.Typer()
memory = Mem0Memory()
react_agent = ReActAgent()

@cli.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to")
):
    """Start the MCP server."""
    console.print(f"Starting MCP server on {host}:{port}", style="bold green")
    uvicorn.run(app, host=host, port=port)

@cli.command()
def solve(
    task: str = typer.Argument(..., help="The coding task to solve"),
    save: bool = typer.Option(True, help="Whether to save the task and solution in memory")
):
    """Solve a coding task using the ReAct agent."""
    async def _solve():
        # Create task
        task_obj = CodingTask(
            task_id=str(uuid.uuid4()),
            description=task,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if save:
            await memory.store(entry={
                "key": f"task_{task_obj.task_id}",
                "content": task_obj.dict(),
                "tags": ["task"]
            })
        
        # Create workflow state and solve
        workflow_state = await react_agent.solve_task(task_obj)
        
        # Display results
        table = Table(title="Task Solution")
        table.add_column("Step", justify="right", style="cyan")
        table.add_column("Thought", style="magenta")
        table.add_column("Action", style="green")
        table.add_column("Observation", style="yellow")
        
        for i, step in enumerate(workflow_state.steps, 1):
            table.add_row(
                str(i),
                step.thought,
                step.action or "-",
                step.observation or "-"
            )
        
        console.print(table)
        
        if workflow_state.current_solution and save:
            await memory.store(entry={
                "key": f"solution_{task_obj.task_id}",
                "content": workflow_state.current_solution.dict(),
                "tags": ["solution"]
            })
            console.print(f"\nSolution saved with ID: {task_obj.task_id}", style="bold green")
    
    asyncio.run(_solve())

@cli.command()
def list_tasks():
    """List all saved tasks."""
    async def _list():
        memories = await memory.retrieve("type:task")
        
        table = Table(title="Saved Tasks")
        table.add_column("ID", style="cyan")
        table.add_column("Description")
        table.add_column("Status", style="green")
        table.add_column("Created", style="magenta")
        
        for mem in memories:
            task = CodingTask(**mem.content)
            table.add_row(
                task.task_id,
                task.description[:50] + "..." if len(task.description) > 50 else task.description,
                task.status.value,
                task.created_at.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        console.print(table)
    
    asyncio.run(_list())

if __name__ == "__main__":
    cli()
