from typing import List, Dict, Any, Optional
from .models import ReActStep, WorkflowState, TaskStatus, MemoryEntry
from .config import settings
from .mem0_memory import Mem0Memory
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime

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
        step = ReActStep(thought="", action=None, action_input=None)
        
        for line in lines:
            if line.startswith("Thought:"):
                step.thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                step.action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                # Try to parse as JSON, fallback to string if not valid JSON
                try:
                    input_str = line.replace("Action Input:", "").strip()
                    step.action_input = eval(input_str)
                except:
                    step.action_input = input_str
        
        return step
    
    def _format_memories(self, memories: List[MemoryEntry]) -> str:
        """Format retrieved memories into a context string."""
        if not memories:
            return "No relevant previous context found."
            
        context_parts = ["Relevant previous context:"]
        for memory in memories:
            context_parts.append(f"- {memory.content}")
        return "\n".join(context_parts)
    
    async def execute_step(self, workflow_state: WorkflowState) -> WorkflowState:
        """Execute a single step in the ReAct loop."""
        if len(workflow_state.steps) >= self.max_steps:
            workflow_state.task.status = TaskStatus.FAILED
            return workflow_state
            
        # Get the next step from the model
        next_step = await self._get_next_step(workflow_state)
        
        # If there's an action, execute it
        if next_step.action:
            # Here you would implement the action execution logic
            # This could involve calling other components of your system
            observation = "Action execution not implemented yet"
            next_step.observation = observation
        
        # Add the step to the workflow
        workflow_state.steps.append(next_step)
        
        # Update task status if needed
        if "FINAL ANSWER:" in next_step.thought:
            workflow_state.task.status = TaskStatus.COMPLETED
            # Store the final outcome as a memory
            memory_entry = MemoryEntry(
                key=workflow_state.task.id,
                content=f"Task: {workflow_state.task.description}\nOutcome: {next_step.thought}",
                tags=["task_completion", "coding"],
                timestamp=datetime.utcnow()
            )
            await self.memory.store(memory_entry)
        
        return workflow_state
    
    async def solve_task(self, workflow_state: WorkflowState) -> WorkflowState:
        """Run the ReAct loop until completion or max steps reached."""
        workflow_state.task.status = TaskStatus.IN_PROGRESS
        
        while workflow_state.task.status == TaskStatus.IN_PROGRESS:
            workflow_state = await self.execute_step(workflow_state)
        
        return workflow_state
