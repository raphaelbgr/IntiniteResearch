# Infinite Research Refinement System - Architecture

## Overview

An autonomous research system that uses Agno agents with RAG capabilities to conduct deep research with parallel workers, continuously refining output documents until manually interrupted.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Orchestrator                         │
│  - Receives user prompts                                         │
│  - Manages research lifecycle                                    │
│  - Coordinates refinement loops                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ├──────────────────────────────────────────────┐
                  │                                              │
         ┌────────▼─────────┐                         ┌─────────▼────────┐
         │  LMStudio Server │                         │  Vector Database │
         │   (localhost)    │                         │   (PgVector/     │
         │    Port: 1234    │                         │    SQLite)       │
         │  OpenAI-compat   │                         └─────────┬────────┘
         └────────┬─────────┘                                   │
                  │                                              │
         ┌────────▼──────────────────────────────────────────────▼──────┐
         │              Agno Agent with RAG                             │
         │  - Knowledge base integration                                │
         │  - Memory management                                         │
         │  - Research coordination                                     │
         └────────┬───────────────────────────────────────────┬─────────┘
                  │                                           │
      ┌───────────▼─────────────┐              ┌─────────────▼──────────┐
      │  Research Worker Pool   │              │   Refinement Engine    │
      │  - Parallel execution   │              │   - Version control    │
      │  - Topic decomposition  │              │   - Quality assessment │
      │  - Data gathering       │              │   - Iterative polish   │
      └───────────┬─────────────┘              └─────────────┬──────────┘
                  │                                           │
                  └─────────────┬─────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   File System Output   │
                    │  /generation/          │
                    │    research-id/        │
                    │      refinement-*.md   │
                    │      rag/              │
                    │      kb/               │
                    └────────────────────────┘
```

## Component Details

### 1. Main Orchestrator (`research_orchestrator.py`)
- Entry point for user prompts
- Generates unique research IDs (timestamp-based)
- Manages infinite refinement loop
- Handles graceful shutdown on interrupt (Ctrl+C)
- Coordinates between workers and refinement

### 2. LMStudio Integration
- **Base URL**: `http://<ip_address>:1234/v1`
- **API**: OpenAI-compatible endpoints
- **Configuration**: Uses Agno's OpenAI model with custom base_url
- Local execution for privacy and speed

### 3. Agno Agent System

#### Main Research Agent
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agno.storage.sqlite import SqliteStorage
```

Features:
- **Knowledge Base**: Combined knowledge sources (documents, URLs, custom data)
- **Vector Database**: Stores embeddings for fast semantic search
- **Memory**: SQLite-backed persistent memory across sessions
- **RAG**: Retrieval-augmented generation for context-aware research

#### Worker Agents (Team)
- Multiple specialized agents for parallel research
- Each worker handles a research subtopic
- Results aggregated by main agent

### 4. Vector Database Options

#### Option A: PgVector (Recommended for production)
- PostgreSQL with pgvector extension
- Supports hybrid search (semantic + keyword)
- Requires PostgreSQL installation

#### Option B: SQLite with sqlite-vec (Lightweight)
- File-based vector storage
- Perfect for local development
- No external dependencies
- Single file database

### 5. Research Workflow

```
User Prompt
    │
    ▼
Generate Research ID (e.g., research-20250121-143022)
    │
    ▼
Create Directory Structure
    │
    ▼
┌───────────────────────────────────────┐
│  Initial Research Phase               │
│  - Decompose topic into subtopics    │
│  - Spawn N parallel worker agents     │
│  - Each worker researches subtopic    │
│  - Workers store findings in vectors  │
└───────────┬───────────────────────────┘
            │
            ▼
Aggregate Worker Results → draft-0001.md
            │
            ▼
┌───────────────────────────────────────┐
│  Refinement Loop (Infinite)           │
│  While not interrupted:               │
│    1. Load previous version           │
│    2. Query vector KB for context     │
│    3. Agent analyzes & improves       │
│    4. Generate new version            │
│    5. Store refined doc in vectors    │
│    6. Increment version number        │
│    7. Sleep briefly                   │
└───────────────────────────────────────┘
```

### 6. Directory Structure

```
/generation/
  ├── research-{timestamp}/
  │   ├── refinement-0001.md    # Initial research output
  │   ├── refinement-0002.md    # First refinement
  │   ├── refinement-0003.md    # Second refinement
  │   ├── ...
  │   ├── refinement-NNNN.md    # Latest version
  │   ├── rag/
  │   │   └── vectors.db        # Vector embeddings (if using SQLite)
  │   ├── kb/
  │   │   ├── knowledge.db      # Knowledge base storage
  │   │   └── metadata.json     # Research metadata
  │   └── memory/
  │       └── agent_memory.db   # Agent conversation memory
```

### 7. Vector Storage Integration

After each refinement:
1. **Chunk the document**: Split into semantic chunks
2. **Generate embeddings**: Using LMStudio's embedding model
3. **Store in vector DB**: With metadata (version, timestamp, research_id)
4. **Enable retrieval**: Future queries can access all versions

Benefits:
- **Token optimization**: Store summaries/embeddings instead of full text
- **Contextual retrieval**: Agent can query past refinements
- **Version comparison**: Semantic search across all versions
- **Knowledge accumulation**: Build research-specific knowledge base

### 8. SQL File Database

For the file-based SQL database requirement:

#### SQLite (Built-in with Agno)
```python
from agno.storage.sqlite import SqliteStorage

storage = SqliteStorage(
    table_name="research_sessions",
    db_file=f"generation/{research_id}/kb/research.db"
)
```

Features:
- Full SQL support (SELECT, JOIN, WHERE, etc.)
- File-based (no server needed)
- ACID compliance
- High performance for local operations
- Used by Agno for agent memory/storage

### 9. Parallel Worker Implementation

```python
from agno.agent import Agent
from agno.teams import Team
import asyncio

# Create worker agents
researchers = [
    Agent(name=f"researcher_{i}", role="Research specialist")
    for i in range(num_workers)
]

# Create team
research_team = Team(
    agents=researchers,
    leader=main_agent,
    mode="parallel"  # Execute tasks in parallel
)

# Execute research
await research_team.run(task=research_prompt)
```

### 10. Refinement Engine

```python
def refine_document(research_id: str, version: int):
    # Load previous version
    prev_doc = load_document(research_id, version - 1)

    # Query vector KB for related context
    context = knowledge_base.search(query=prev_doc[:500], limit=10)

    # Agent refines with context
    refined = agent.run(
        f"Refine this research document:\n\n{prev_doc}\n\n"
        f"Related context:\n{context}\n\n"
        f"Make it more comprehensive, accurate, and well-structured."
    )

    # Save new version
    save_document(research_id, version, refined)

    # Add to vector KB
    add_to_knowledge_base(research_id, version, refined)

    return refined
```

## Technology Stack

- **Language**: Python 3.10+
- **Framework**: Agno (agno-agi)
- **LLM Server**: LMStudio (OpenAI-compatible)
- **Vector DB**: SQLite with sqlite-vec OR PgVector
- **Storage**: SQLite (for memory/sessions)
- **Async**: asyncio for parallel workers

## Installation Requirements

```bash
pip install agno
pip install agno[lmstudio]  # LMStudio integration
pip install openai  # For OpenAI-compatible client
pip install pgvector  # If using PostgreSQL
pip install sqlite-vec  # If using SQLite vectors
pip install asyncio
pip install aiofiles  # Async file operations
```

## Configuration

Create `config.yaml`:
```yaml
lmstudio:
  base_url: "http://<ip_address>:1234/v1"
  api_key: "lm-studio"  # Dummy key for compatibility
  model: "local-model"  # Your loaded model name

research:
  num_workers: 5  # Parallel research workers
  refinement_delay: 10  # Seconds between refinements
  output_dir: "./generation"

vector_db:
  type: "sqlite"  # or "pgvector"
  embedding_model: "local-embedding-model"
  chunk_size: 512
  chunk_overlap: 50

storage:
  type: "sqlite"
  base_dir: "./generation"
```

## Usage Flow

1. **Start**: `python research_orchestrator.py "Your research topic here"`
2. **Initial Research**: Workers gather information in parallel
3. **First Draft**: Compiled into `refinement-0001.md`
4. **Infinite Refinement**: Continuously improves until Ctrl+C
5. **Vector Storage**: Each version embedded and stored for future queries
6. **Resume**: Can query past research via vector search

## Key Features

✓ Local LLM execution (privacy)
✓ Parallel research workers (speed)
✓ Infinite refinement loop (quality)
✓ Version control (traceability)
✓ Vector storage (efficient retrieval)
✓ File-based SQL (simplicity)
✓ RAG integration (context-aware)
✓ Graceful shutdown (data safety)

## Future Enhancements

- Web UI for monitoring progress
- Real-time streaming of refinements
- Multi-document output (split by topics)
- Automatic source citation
- Research quality metrics
- Collaborative multi-user research
