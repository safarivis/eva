from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
import json
from .models import MemoryEntry
from .config import settings
from mem0 import AsyncMemoryClient as AsyncMem0Client

class Mem0Memory:
    def __init__(self):
        self.client = AsyncMem0Client(api_key=settings.MEM0_API_KEY)
    
    async def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry in Mem0."""
        try:
            result = await self.client.create_memory(
                content=entry.content,
                tags=entry.tags,
                metadata={
                    "timestamp": entry.timestamp.isoformat(),
                    "key": entry.key
                }
            )
            return result.id
        except Exception as e:
            raise Exception(f"Failed to store memory: {str(e)}")
    
    async def retrieve(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Retrieve relevant memories based on a query."""
        try:
            results = await self.client.search_memories(
                query=query,
                limit=limit,
                include_metadata=True
            )
            
            memories = []
            for result in results:
                memory = MemoryEntry(
                    key=result.metadata["key"],
                    content=result.content,
                    tags=result.tags,
                    timestamp=datetime.fromisoformat(result.metadata["timestamp"])
                )
                memories.append(memory)
            return memories
        except Exception as e:
            raise Exception(f"Failed to retrieve memories: {str(e)}")
    
    async def update(self, memory_id: str, entry: MemoryEntry) -> None:
        """Update an existing memory entry."""
        try:
            await self.client.update_memory(
                memory_id=memory_id,
                content=entry.content,
                tags=entry.tags,
                metadata={
                    "timestamp": entry.timestamp.isoformat(),
                    "key": entry.key
                }
            )
        except Exception as e:
            raise Exception(f"Failed to update memory: {str(e)}")
    
    async def delete(self, memory_id: str) -> None:
        """Delete a memory entry."""
        try:
            await self.client.delete_memory(memory_id=memory_id)
        except Exception as e:
            raise Exception(f"Failed to delete memory: {str(e)}")
            
    async def get_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory by ID."""
        try:
            result = await self.client.get_memory(memory_id)
            if result:
                return MemoryEntry(
                    key=result.metadata["key"],
                    content=result.content,
                    tags=result.tags,
                    timestamp=datetime.fromisoformat(result.metadata["timestamp"])
                )
            return None
        except Exception as e:
            raise Exception(f"Failed to get memory: {str(e)}")
