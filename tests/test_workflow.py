"""Test workflow functionality."""
import pytest
from datetime import datetime, timezone
from agent.models import CodingTask, WorkflowState, ReActStep, TaskStatus
from agent.workflow import (
    create_workflow_graph, generate_step, execute_step, 
    handle_error, validate_state, calculate_backoff
)
from unittest.mock import AsyncMock, patch
import asyncio
from langgraph.graph import END

@pytest.fixture
def mock_react_agent():
    agent = AsyncMock()
    agent._get_next_step.return_value = ReActStep(
        thought="Test thought",
        action="test_action",
        action_input={"test": "data"},
        observation=None
    )
    agent.execute_step.return_value = "Test observation"
    return agent

@pytest.fixture
def workflow_graph(mock_react_agent):
    """Create a workflow graph for testing."""
    return create_workflow_graph()

@pytest.mark.asyncio
async def test_workflow_graph_creation(workflow_graph):
    """Test workflow graph creation."""
    assert workflow_graph is not None
    assert workflow_graph.config == {"recursion_limit": 100}

@pytest.mark.asyncio
async def test_workflow_execution(workflow_graph, mock_react_agent):
    """Test workflow execution."""
    # Create task with mutable status
    task = CodingTask(
        task_id="test_workflow_1",
        description="Test workflow",
        status=TaskStatus.PENDING,
        created_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        updated_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        context={},
        model_config={'frozen': False}
    )

    initial_state = WorkflowState(
        task=task,
        steps=[],
        current_solution=None,
        memory_context=[],
        agent=mock_react_agent
    )

    # Mock the step generation to return a finish action
    mock_react_agent._get_next_step.return_value = ReActStep(
        thought="Finished",
        action="finish",
        action_input={},
        observation=None
    )
    mock_react_agent.execute_step.return_value = "Task completed"

    # Run the workflow
    final_state = None
    async for state in workflow_graph.astream(initial_state):
        if isinstance(state, dict):
            current_state = state.get("state")
        else:
            current_state = state
        if isinstance(current_state, WorkflowState) and current_state.task.status == TaskStatus.COMPLETED:
            final_state = current_state
            break
    assert final_state is not None, "Workflow did not complete successfully"

    assert final_state is not None
    assert isinstance(final_state, WorkflowState)
    assert final_state.task.status == TaskStatus.COMPLETED

@pytest.mark.asyncio
async def test_state_validation():
    """Test state validation function."""
    # Test with valid state
    task = CodingTask(
        task_id="test_validation",
        description="Test validation",
        status=TaskStatus.PENDING,
        created_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        updated_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        context={},
        model_config={'frozen': False}
    )
    
    valid_state = WorkflowState(
        task=task,
        steps=[],
        current_solution=None,
        memory_context=[],
        agent=AsyncMock()
    )
    assert validate_state(valid_state) is None

    # Test with missing agent
    invalid_state = WorkflowState(
        task=task,
        steps=[],
        current_solution=None,
        memory_context=[],
        agent=None
    )
    assert validate_state(invalid_state) == "Missing agent in state"

@pytest.mark.asyncio
async def test_exponential_backoff():
    """Test exponential backoff calculation."""
    assert calculate_backoff(0) == 1000  # Initial delay
    assert calculate_backoff(1) == 2000  # Second attempt
    assert calculate_backoff(2) == 4000  # Third attempt
    assert calculate_backoff(10) == 30000  # Max delay cap

@pytest.mark.asyncio
async def test_error_handling_with_retries(workflow_graph, mock_react_agent):
    """Test error handling with retries."""
    task = CodingTask(
        task_id="test_error_handling",
        description="Test error handling",
        status=TaskStatus.PENDING,
        created_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        updated_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        context={"retry_count": 0},
        model_config={'frozen': False}
    )

    state = WorkflowState(
        task=task,
        steps=[],
        current_solution=None,
        memory_context=[],
        agent=mock_react_agent,
        error="Test error"
    )

    # Test first retry
    updates = await handle_error(state)
    assert updates["next"] == "should_continue"
    assert updates["state"].task.context["retry_count"] == 1

    # Test max retries
    state.task.context["retry_count"] = 3
    with patch('agent.workflow.interrupt') as mock_interrupt:
        mock_interrupt.return_value = {"action": "fail"}
        updates = await handle_error(state)
        assert mock_interrupt.called
        assert updates["next"] == "end"

@pytest.mark.asyncio
async def test_human_intervention(workflow_graph, mock_react_agent):
    """Test human intervention in error handling."""
    task = CodingTask(
        task_id="test_human_intervention",
        description="Test human intervention",
        status=TaskStatus.PENDING,
        created_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        updated_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=timezone.utc),
        context={"retry_count": 3},
        model_config={'frozen': False}
    )

    state = WorkflowState(
        task=task,
        steps=[],
        current_solution=None,
        memory_context=[],
        agent=mock_react_agent,
        error="Critical error"
    )

    # Test human intervention failure
    with patch('agent.workflow.interrupt', side_effect=Exception("Connection error")):
        updates = await handle_error(state)
        assert updates["next"] == "end"
