import os
import pytest
from unittest.mock import patch

# Set test environment variables before any imports
os.environ["MEM0_API_KEY"] = "test_mem0_key"
os.environ["OPENROUTER_API_KEY"] = "test_openrouter_key"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["MAX_RETRIES"] = "3"
os.environ["MAX_REACT_STEPS"] = "6"
os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"

@pytest.fixture(autouse=True)
def mock_api_validation():
    """Mock API key validation for all tests."""
    with patch('mem0.client.main.MemoryClient._validate_api_key') as mock:
        mock.return_value = "test@example.com"
        yield mock

@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up environment variables after tests."""
    yield
    
    os.environ.pop("MEM0_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("LOG_LEVEL", None)
    os.environ.pop("MAX_RETRIES", None)
    os.environ.pop("MAX_REACT_STEPS", None)
    os.environ.pop("OPENAI_MODEL", None)