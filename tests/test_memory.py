import pytest
from unittest.mock import Mock, patch, AsyncMock
from agent.mem0_memory import Mem0Memory
from agent.models import MemoryEntry
from datetime import datetime

@pytest.fixture
def mock_mem0_client():
    with patch('agent.mem0_memory.AsyncMem0Client') as mock_client:
        # Create a mock instance
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        
        # Setup mock responses
        mock_instance.create_memory.return_value = Mock(
            id='test-id-123',
            content={'data': 'test content'},
            tags=['test'],
            metadata={
                'timestamp': '2025-03-03T08:56:44+02:00',
                'key': 'test-key'
            }
        )
        
        mock_instance.search_memories.return_value = [Mock(
            id='test-id-123',
            content={'data': 'test content'},
            tags=['test'],
            metadata={
                'timestamp': '2025-03-03T08:56:44+02:00',
                'key': 'test-key'
            }
        )]
        
        yield mock_instance

@pytest.fixture
def memory_client(mock_mem0_client):
    return Mem0Memory()

@pytest.mark.asyncio
async def test_store_memory(memory_client, mock_mem0_client):
    entry = MemoryEntry(
        key='test-key',
        content={'data': 'test content'},
        tags=['test'],
        timestamp=datetime.fromisoformat('2025-03-03T08:56:44+02:00')
    )
    
    memory_id = await memory_client.store(entry)
    
    assert memory_id == 'test-id-123'
    
    # Verify the mock was called correctly
    mock_mem0_client.create_memory.assert_awaited_once_with(
        content={'data': 'test content'},
        tags=['test'],
        metadata={
            'timestamp': '2025-03-03T08:56:44+02:00',
            'key': 'test-key'
        }
    )

@pytest.mark.asyncio
async def test_retrieve_memories(memory_client, mock_mem0_client):
    memories = await memory_client.retrieve('test query')
    
    assert len(memories) == 1
    assert isinstance(memories[0], MemoryEntry)
    assert memories[0].key == 'test-key'
    assert memories[0].content == {'data': 'test content'}
    assert memories[0].tags == ['test']
    
    mock_mem0_client.search_memories.assert_awaited_once_with(
        query='test query',
        limit=5,
        include_metadata=True
    )
