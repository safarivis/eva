from typing import List, Dict, Any, Optional
from .models import ReActStep, WorkflowState, TaskStatus, MemoryEntry, CodingTask
from .config import settings
from .mem0_memory import Mem0Memory
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime
import os

class ReActAgent:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.max_steps = settings.MAX_REACT_STEPS
        self.memory = Mem0Memory()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _get_next_step(self, workflow_state: WorkflowState) -> ReActStep:
        """Generate the next reasoning step using the OpenAI API."""
        # Construct the prompt with the task and previous steps
        prompt = self._construct_prompt(workflow_state)
        
        # Retrieve relevant memories for context
        memories = await self.memory.retrieve(workflow_state.task.description)
        context = self._format_memories(memories)
        
        response = await self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a ReAct agent that helps solve coding tasks. Think step by step."},
                {"role": "user", "content": f"{context}\n\n{prompt}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Parse the response into a ReActStep
        return self._parse_response(response.choices[0].message.content)
    
    def _construct_prompt(self, workflow_state: WorkflowState) -> str:
        """Construct the prompt for the next step based on the workflow state."""
        prompt_parts = [
            f"Task: {workflow_state.task.description}\n",
            "Previous steps:"
        ]
        
        for step in workflow_state.steps:
            prompt_parts.append(f"Thought: {step.thought}")
            if step.action:
                prompt_parts.append(f"Action: {step.action}")
                prompt_parts.append(f"Action Input: {step.action_input}")
            if step.observation:
                prompt_parts.append(f"Observation: {step.observation}")
        
        prompt_parts.append("\nWhat should be the next step? Respond in the format:")
        prompt_parts.append("Thought: [your reasoning]")
        prompt_parts.append("Action: [action to take, if any]")
        prompt_parts.append("Action Input: [input for the action, if any]")
        
        return "\n".join(prompt_parts)
    
    def _parse_response(self, response: str) -> ReActStep:
        """Parse the API response into a ReActStep object."""
        lines = response.strip().split("\n")
        thought = ""
        action = ""
        action_input = {}

        for line in lines:
            if line.startswith("Thought:"):
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                action = line[7:].strip()
            elif line.startswith("Action Input:"):
                try:
                    action_input = eval(line[12:].strip())
                except:
                    action_input = {}

        return ReActStep(
            thought=thought or "No thought provided",
            action=action or "finish",
            action_input=action_input
        )
    
    def _format_memories(self, memories: List[MemoryEntry]) -> str:
        """Format retrieved memories into a context string."""
        if not memories:
            return "No relevant previous context found."
            
        context_parts = ["Relevant previous context:"]
        for memory in memories:
            context_parts.append(f"- {memory.content}")
        return "\n".join(context_parts)
    
    async def execute_step(self, step: ReActStep, workflow_state: WorkflowState) -> str:
        """Execute a ReAct step."""
        # Check if we've reached max steps
        if len(workflow_state.steps) >= self.max_steps:
            return "Max steps reached"

        # Execute the action based on the step
        if step.action == "write_test":
            return await self._write_test(step.action_input)
        elif step.action == "write_code":
            return await self._write_code(step.action_input)
        elif step.action == "run_test":
            return await self._run_test(step.action_input)
        else:
            return f"Unknown action: {step.action}"

    async def solve_task(self, workflow_state: WorkflowState) -> WorkflowState:
        """Main solving loop."""
        try:
            # Create a new task instance to allow mutation
            workflow_state.task = CodingTask(
                task_id=workflow_state.task.task_id,
                description=workflow_state.task.description,
                status=TaskStatus.IN_PROGRESS,
                created_at=workflow_state.task.created_at,
                updated_at=workflow_state.task.updated_at,
                context=workflow_state.task.context,
                model_config={'frozen': False}
            )

            while True:
                # Get next step
                next_step = await self._get_next_step(workflow_state)
                workflow_state.steps.append(next_step)

                # Execute step
                observation = await self.execute_step(next_step, workflow_state)
                next_step.observation = observation

                # Update task status based on step action
                if next_step.action == "finish":
                    workflow_state.task = CodingTask(
                        task_id=workflow_state.task.task_id,
                        description=workflow_state.task.description,
                        status=TaskStatus.COMPLETED,
                        created_at=workflow_state.task.created_at,
                        updated_at=workflow_state.task.updated_at,
                        context=workflow_state.task.context,
                        model_config={'frozen': False}
                    )
                    break

                # Check if we're done
                if len(workflow_state.steps) >= self.max_steps:
                    workflow_state.task = CodingTask(
                        task_id=workflow_state.task.task_id,
                        description=workflow_state.task.description,
                        status=TaskStatus.FAILED,
                        created_at=workflow_state.task.created_at,
                        updated_at=workflow_state.task.updated_at,
                        context=workflow_state.task.context,
                        model_config={'frozen': False}
                    )
                    break

            return workflow_state

        except Exception as e:
            # Create a new task instance with failed status
            workflow_state.task = CodingTask(
                task_id=workflow_state.task.task_id,
                description=workflow_state.task.description,
                status=TaskStatus.FAILED,
                created_at=workflow_state.task.created_at,
                updated_at=workflow_state.task.updated_at,
                context=workflow_state.task.context,
                model_config={'frozen': False}
            )
            return workflow_state

    async def _write_test(self, input_data: dict) -> str:
        """Write a test file."""
        # Implementation would go here
        return "Test written successfully"

    async def _write_code(self, input_data: dict) -> str:
        """Write code to implement functionality."""
        # Implementation would go here
        return "Code written successfully"

    async def _run_test(self, input_data: dict) -> str:
        """Run tests and return results."""
        # Implementation would go here
        return "Tests passed successfully"
