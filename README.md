# Eva AI Assistant

Eva is an intelligent AI agent that combines ReAct architecture with Mem0-based persistent memory for enhanced reasoning and learning capabilities.

## Features

- **ReAct Architecture:** Advanced reasoning and action loop for complex problem-solving
- **Mem0 Memory:** Cloud-based persistent memory with semantic search
- **Contextual Learning:** Learns from past experiences to improve future decisions
- **Async Design:** Built for optimal performance with async/await patterns
- **Type-Safe:** Leverages Python type hints and Pydantic models

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv eva-agent
source eva-agent/bin/activate  # Linux/Mac
# or
.\eva-agent\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
MEM0_API_KEY=your_mem0_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
LOG_LEVEL=INFO
MAX_RETRIES=3
MAX_REACT_STEPS=6
```

## Usage

### Python Interface

```python
from eva import ReActAgent
from eva.memory import Mem0Memory

# Initialize Eva
memory = Mem0Memory(api_key=os.getenv("MEM0_API_KEY"))
eva = ReActAgent(memory=memory)

# Execute a task
result = await eva.attempt_completion("Your task description")
```

### Memory Operations

```python
# Store a memory
await memory.store(
    task_description="Calculate fibonacci sequence",
    outcome="Successfully implemented recursive solution",
    tags=["mathematics", "recursion"]
)

# Retrieve relevant memories
memories = await memory.search_memories("fibonacci implementation")
```

## Project Structure

```
eva/
├── __init__.py
├── agent.py          # ReAct agent implementation
├── memory.py         # Mem0 memory integration
├── models.py         # Pydantic models
├── tools/            # Available tools and actions
│   └── __init__.py
├── utils/            # Helper utilities
│   └── __init__.py
├── requirements.txt
└── .env
```

## Memory Architecture

Eva uses Mem0 for advanced memory management and learning capabilities:

### Core Memory Features

- **Persistent Storage:** 
  - Stores task outcomes, experiences, and metadata
  - Maintains timestamps and unique task IDs
  - Supports tagging for better organization

- **Semantic Retrieval:** 
  - Advanced semantic search for finding relevant past experiences
  - Context-aware memory retrieval during task execution
  - Efficient ranking and filtering of memories

- **Context Enhancement:**
  - Incorporates historical context in each reasoning step
  - Formats memories for optimal decision-making
  - Maintains task continuity through persistent storage

### Technical Implementation

- **CRUD Operations:**
  - Async implementation for optimal performance
  - Comprehensive error handling
  - Bulk operations support

- **Integration Points:**
  - Seamless integration with ReAct reasoning loop
  - Memory-aware decision making in `_get_next_step`
  - Context formatting via `_format_memories`

- **Performance Features:**
  - Asynchronous operations for better scalability
  - Efficient memory indexing and retrieval
  - Optimized context window management

## Development

### Running Tests

```bash
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
