import pytest
from unittest.mock import AsyncMock, patch
from agent.dspy_modules import AsyncOpenAIWrapper, CodeAnalyzer, CodeGenerator, TestGenerator

@pytest.fixture
def mock_openai_client():
    with patch('openai.AsyncOpenAI') as mock:
        mock_instance = AsyncMock()
        mock_instance.chat.completions.create.return_value.choices = [
            AsyncMock(message=AsyncMock(content="Test completion"))
        ]
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def code_analyzer(mock_openai_client):
    analyzer = CodeAnalyzer()
    analyzer.lm = mock_openai_client
    return analyzer

@pytest.fixture
def code_generator(mock_openai_client):
    generator = CodeGenerator()
    generator.lm = mock_openai_client
    return generator

@pytest.fixture
def test_generator(mock_openai_client):
    generator = TestGenerator()
    generator.lm = mock_openai_client
    return generator

@pytest.mark.asyncio
async def test_async_openai_wrapper_init(mock_openai_client):
    wrapper = AsyncOpenAIWrapper()
    assert wrapper.client is not None

@pytest.mark.asyncio
async def test_async_openai_wrapper_forward(mock_openai_client):
    wrapper = AsyncOpenAIWrapper()
    result = await wrapper.forward(prompt="Test prompt")
    assert result == "Test completion"

@pytest.mark.asyncio
async def test_code_analyzer(code_analyzer):
    result = await code_analyzer.analyze_code("def test(): pass")
    assert isinstance(result, str)
    assert result == "Test completion"

@pytest.mark.asyncio
async def test_code_generator(code_generator):
    result = await code_generator.generate_code("Create a test function")
    assert isinstance(result, str)
    assert result == "Test completion"

@pytest.mark.asyncio
async def test_test_generator(test_generator):
    result = await test_generator.generate_test("def test(): pass")
    assert isinstance(result, str)
    assert result == "Test completion"
