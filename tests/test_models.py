from datetime import datetime
from agent.models import CodingTask, CodeSolution, MemoryEntry, ReActStep, WorkflowState, TaskStatus

def test_coding_task_creation():
    task = CodingTask(
        task_id="task1",
        description="Test task"
    )
    assert task.task_id == "task1"
    assert task.description == "Test task"
    assert task.status == TaskStatus.PENDING
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)

def test_code_solution_creation():
    solution = CodeSolution(
        task_id="task1",
        code="print('hello')",
        explanation="Simple print statement"
    )
    assert solution.task_id == "task1"
    assert solution.code == "print('hello')"
    assert solution.explanation == "Simple print statement"
    assert solution.dependencies == []
    assert isinstance(solution.created_at, datetime)

def test_memory_entry_creation():
    memory = MemoryEntry(
        key="test_key",
        content={"data": "test content"},
        tags=["test"]
    )
    assert memory.key == "test_key"
    assert memory.content["data"] == "test content"
    assert memory.tags == ["test"]
    assert isinstance(memory.timestamp, datetime)

def test_react_step_creation():
    step = ReActStep(
        thought="I should test this",
        action="run_test",
        action_input={"test_name": "unit_test"}
    )
    assert step.thought == "I should test this"
    assert step.action == "run_test"
    assert step.action_input["test_name"] == "unit_test"
    assert step.observation is None

def test_workflow_state():
    task = CodingTask(
        task_id="task1",
        description="Test task"
    )
    state = WorkflowState(task=task)
    assert state.task.task_id == "task1"
    assert state.steps == []
    assert state.current_solution is None
    assert state.memory_context == []
