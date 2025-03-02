import pytest
from unittest.mock import Mock, patch
from agent.mem0_memory import Mem0Memory
from agent.models import MemoryEntry

@pytest.fixture
def mock_mem0_client():
    with patch('mem0.Client') as mock_client:
        # Create a mock instance
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Setup mock responses
        mock_instance.create_memory.return_value = {
            'id': 'test-id-123',
            'content': 'test content',
            'metadata': {'tags': ['test']}
        }
        
        mock_instance.search.return_value = [{
            'id': 'test-id-123',
            'content': 'test content',
            'metadata': {'tags': ['test']}
        }]
        
        yield mock_instance

@pytest.fixture
def memory_client(mock_mem0_client):
    return Mem0Memory()

@pytest.mark.asyncio
async def test_add_memory(memory_client, mock_mem0_client):
    memory = await memory_client.add_memory(
        content='test content',
        metadata={'tags': ['test']}
    )
    
    assert isinstance(memory, MemoryEntry)
    assert memory.key == 'test-id-123'
    assert memory.content['data'] == 'test content'
    assert memory.tags == ['test']
    
    # Verify the mock was called correctly
    mock_mem0_client.create_memory.assert_called_once_with(
        content='test content',
        metadata={'tags': ['test']}
    )

@pytest.mark.asyncio
async def test_search_memories(memory_client, mock_mem0_client):
    results = await memory_client.search_memories('test query', limit=5)
    
    assert len(results) > 0
    assert isinstance(results[0], MemoryEntry)
    assert results[0].key == 'test-id-123'
    
    # Verify the mock was called correctly
    mock_mem0_client.search.assert_called_once_with('test query', limit=5)

@pytest.mark.asyncio
async def test_get_recent_memories(memory_client, mock_mem0_client):
    mock_mem0_client.list_memories.return_value = [{
        'id': f'test-id-{i}',
        'content': f'test content {i}',
        'metadata': {'tags': ['test']}
    } for i in range(3)]
    
    results = await memory_client.get_recent_memories(n=3)
    
    assert len(results) == 3
    assert all(isinstance(r, MemoryEntry) for r in results)
    assert [r.key for r in results] == ['test-id-0', 'test-id-1', 'test-id-2']
    
    # Verify the mock was called correctly
    mock_mem0_client.list_memories.assert_called_once_with(limit=3)
