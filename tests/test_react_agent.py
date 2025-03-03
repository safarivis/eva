import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from agent.models import CodingTask, WorkflowState, ReActStep, TaskStatus
from agent.react_loop import ReActAgent
from agent.mem0_memory import Mem0Memory

@pytest.fixture
def mock_memory():
    with patch('agent.mem0_memory.Mem0Memory') as mock:
        mock_instance = AsyncMock()
        mock_instance.retrieve.return_value = []
        mock_instance.store.return_value = None
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_openai():
    with patch('openai.AsyncOpenAI') as mock:
        mock_instance = AsyncMock()
        mock_instance.chat.completions.create.return_value.choices = [
            AsyncMock(message=AsyncMock(content="Thought: Test thought\nAction: test_action\nAction Input: {}"))
        ]
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def react_agent(mock_openai, mock_memory):
    agent = ReActAgent()
    agent.memory = mock_memory
    return agent

@pytest.fixture
def workflow_state(react_agent):
    task = CodingTask(
        task_id="test_task_1",
        description="Test task",
        status=TaskStatus.PENDING,
        created_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        updated_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        context={},
        model_config={'frozen': False}
    )
    return WorkflowState(
        task=task,
        steps=[],
        current_solution=None,
        memory_context=[],
        agent=react_agent
    )

@pytest.mark.asyncio
async def test_get_next_step(react_agent, workflow_state, mock_openai):
    step = await react_agent._get_next_step(workflow_state)
    assert isinstance(step, ReActStep)
    assert step.thought == "Test thought"
    assert step.action == "test_action"

@pytest.mark.asyncio
async def test_execute_step(react_agent, workflow_state):
    step = ReActStep(
        thought="Test step",
        action="test_action",
        action_input={"test": "data"},
        observation=None
    )
    observation = await react_agent.execute_step(step, workflow_state)
    assert isinstance(observation, str)

@pytest.mark.asyncio
async def test_solve_task(react_agent, workflow_state, mock_openai):
    # Create a new task instance to avoid frozen state
    task = CodingTask(
        task_id=workflow_state.task.task_id,
        description=workflow_state.task.description,
        status=TaskStatus.PENDING,
        created_at=workflow_state.task.created_at,
        updated_at=workflow_state.task.updated_at,
        context={},
        model_config={'frozen': False}  # Make task mutable
    )
    workflow_state.task = task

    # Mock the next step to finish immediately
    mock_openai.chat.completions.create.return_value.choices = [
        AsyncMock(message=AsyncMock(content="Thought: Finished\nAction: finish\nAction Input: {}"))
    ]

    result = await react_agent.solve_task(workflow_state)
    assert isinstance(result, WorkflowState)
    assert result.task.status == TaskStatus.COMPLETED
