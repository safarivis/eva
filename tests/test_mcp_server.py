import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone as tz
from agent.mcp_server import MCPServer
from agent.models import CodingTask, TaskStatus, WorkflowState, ReActStep
from agent.mem0_memory import Mem0Memory

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
def mock_react_agent():
    with patch('agent.mcp_server.ReActAgent') as mock:
        mock_instance = AsyncMock()
        mock_instance.solve_task.return_value = WorkflowState(
            task=CodingTask(
                task_id="test_task",
                description="Test task",
                status=TaskStatus.COMPLETED,
                created_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=tz.utc),
                updated_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=tz.utc),
                context={},
                model_config={'frozen': False}
            ),
            steps=[
                ReActStep(
                    thought="Test step",
                    action="test_action",
                    action_input={"test": "data"},
                    observation="Test observation"
                )
            ],
            current_solution=None,
            memory_context=[],
            agent=mock_instance
        )
        yield mock_instance

@pytest.fixture
def mock_memory():
    with patch('agent.mcp_server.Mem0Memory') as mock:
        mock_instance = AsyncMock()
        mock_instance.get_task.return_value = CodingTask(
            task_id="test_task",
            description="Test task",
            status=TaskStatus.PENDING,
            created_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=tz.utc),
            updated_at=datetime(2025, 3, 3, 9, 59, 34, tzinfo=tz.utc),
            context={},
            model_config={'frozen': False}
        )
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mcp_server(mock_react_agent, mock_memory, mock_openai):
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        return MCPServer(mock_react_agent, mock_memory)

@pytest.mark.asyncio
async def test_create_task(mcp_server, mock_memory):
    task = await mcp_server.create_task("Test task")
    assert isinstance(task, CodingTask)
    assert task.description == "Test task"
    assert task.status == TaskStatus.PENDING

@pytest.mark.asyncio
async def test_get_task(mcp_server, mock_memory):
    task = await mcp_server.get_task("test_task")
    assert isinstance(task, CodingTask)
    assert task.task_id == "test_task"

@pytest.mark.asyncio
async def test_solve_task(mcp_server, mock_memory, mock_react_agent):
    task = await mcp_server.solve_task("test_task")
    assert isinstance(task, CodingTask)
    assert task.status == TaskStatus.COMPLETED

@pytest.mark.asyncio
async def test_health_check(mcp_server):
    result = await mcp_server.health_check()
    assert result == {"status": "ok"}
