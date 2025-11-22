# Project Structure

```
InfiniteResearch/
│
├── research_orchestrator.py    # Main entry point - run this
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── .gitignore                   # Git ignore rules
│
├── README.md                    # Full documentation
├── ARCHITECTURE.md              # System architecture
├── QUICKSTART.md               # Quick start guide
├── PROJECT_STRUCTURE.md        # This file
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── config_loader.py        # YAML config loading
│   └── logger.py               # Logging setup
│
├── storage/                     # Storage and database
│   ├── __init__.py
│   ├── file_manager.py         # File system operations
│   └── vector_store.py         # Vector database (SQLite/PgVector)
│
├── agents/                      # Agno agent implementations
│   ├── __init__.py
│   ├── research_agent.py       # Main research agent with RAG
│   └── worker_pool.py          # Parallel research workers
│
├── refinement/                  # Document refinement
│   ├── __init__.py
│   └── refiner.py              # Refinement engine
│
└── generation/                  # Output directory (created at runtime)
    └── research-{timestamp}/
        ├── refinement-0001.md
        ├── refinement-0002.md
        ├── refinement-NNNN.md
        ├── rag/
        │   └── vectors.db
        ├── kb/
        │   ├── knowledge.db
        │   ├── knowledge.txt
        │   └── metadata.json
        ├── memory/
        │   └── agent_memory.db
        └── logs/
            └── research.log
```

## Module Descriptions

### Core Modules

#### `research_orchestrator.py`
- **Purpose**: Main entry point for the system
- **Responsibilities**:
  - Parse command-line arguments
  - Initialize all components
  - Orchestrate research workflow
  - Handle graceful shutdown
- **Usage**: `python research_orchestrator.py "topic"`

### Utility Modules (`utils/`)

#### `config_loader.py`
- Load and parse YAML configuration
- Extract specific config sections
- Validate configuration values

#### `logger.py`
- Setup Rich logging with colors
- Console and file logging
- Different log levels (DEBUG, INFO, WARNING, ERROR)

### Storage Modules (`storage/`)

#### `file_manager.py`
- **Purpose**: Manage file system operations
- **Key Functions**:
  - `create_research_id()`: Generate unique research IDs
  - `create_research_directory()`: Setup directory structure
  - `save_refinement()`: Save document versions
  - `load_refinement()`: Load document versions
  - `get_latest_version()`: Get current version number
  - `save_metadata()` / `load_metadata()`: Manage research metadata

#### `vector_store.py`
- **Purpose**: Vector database for RAG
- **Key Functions**:
  - `add_document_chunks()`: Store text chunks with embeddings
  - `search_similar()`: Semantic search
  - `get_all_chunks()`: Retrieve all stored chunks
- **Backends**: SQLite (default), PgVector (optional)

### Agent Modules (`agents/`)

#### `research_agent.py`
- **Purpose**: Main research agent with Agno
- **Key Features**:
  - LMStudio integration via OpenAI API
  - RAG capabilities with knowledge base
  - SQLite storage for memory
  - Session management
- **Key Functions**:
  - `research()`: Conduct initial research
  - `refine()`: Refine existing documents
  - `add_knowledge()`: Update knowledge base

#### `worker_pool.py`
- **Purpose**: Manage parallel research workers
- **Key Features**:
  - Create multiple worker agents
  - Decompose topics into subtopics
  - Execute parallel research
  - Aggregate results
- **Key Functions**:
  - `research_parallel()`: Execute parallel research
  - `decompose_topic()`: Break down main topic
  - `aggregate_results()`: Combine worker outputs

### Refinement Modules (`refinement/`)

#### `refiner.py`
- **Purpose**: Iterative document refinement
- **Key Features**:
  - Infinite refinement loop
  - Context retrieval from vector DB
  - Version management
  - Graceful interruption handling
- **Key Functions**:
  - `refine_once()`: Single refinement iteration
  - `refine_infinite()`: Continuous refinement loop
  - `_chunk_document()`: Split documents for vector storage

## Data Flow

```
1. User runs: python research_orchestrator.py "topic"
                          ↓
2. ResearchOrchestrator initializes all components
                          ↓
3. WorkerPool.research_parallel()
   - Creates 5 worker agents
   - Each researches a subtopic
   - Results aggregated
                          ↓
4. FileManager.save_refinement() → refinement-0001.md
                          ↓
5. VectorStore.add_document_chunks() → vectors.db
                          ↓
6. RefinementEngine.refine_infinite()
   │
   └─→ Loop:
       ├─ Load previous version
       ├─ Query vector DB for context
       ├─ ResearchAgent.refine()
       ├─ Save new version (refinement-NNNN.md)
       ├─ Add to vector store
       ├─ Update knowledge base
       ├─ Wait (refinement_delay seconds)
       └─ Repeat until Ctrl+C
```

## Configuration Flow

```
config.yaml
    │
    ├─→ lmstudio: → ResearchAgent, WorkerPool
    │   ├─ base_url
    │   ├─ model
    │   ├─ temperature
    │   └─ max_tokens
    │
    ├─→ research: → ResearchOrchestrator, WorkerPool
    │   ├─ num_workers
    │   ├─ refinement_delay
    │   └─ output_dir
    │
    ├─→ vector_db: → VectorStore
    │   ├─ type (sqlite/pgvector)
    │   ├─ chunk_size
    │   └─ chunk_overlap
    │
    ├─→ storage: → ResearchAgent, FileManager
    │   ├─ type
    │   ├─ memory_db
    │   └─ knowledge_db
    │
    └─→ logging: → Logger
        ├─ level
        ├─ file
        └─ console
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────┐
│ ResearchOrchestrator (Main Controller)                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ FileManager  │  │ VectorStore  │  │ ResearchAgent    │ │
│  │              │  │              │  │                  │ │
│  │ - Versions   │  │ - Embeddings │  │ - LMStudio      │ │
│  │ - Metadata   │  │ - RAG search │  │ - Knowledge     │ │
│  │ - Directory  │  │ - Chunks     │  │ - Memory        │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
│         │                  │                    │           │
│         └──────────────────┼────────────────────┘           │
│                            │                                │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐ │
│  │ WorkerPool   │  │ Refiner       │  │ Config/Logger   │ │
│  │              │  │               │  │                 │ │
│  │ - 5 workers  │  │ - Loop        │  │ - YAML config   │ │
│  │ - Parallel   │  │ - Versions    │  │ - Rich logging  │ │
│  │ - Aggregate  │  │ - Context     │  │ - Error handling│ │
│  └──────────────┘  └───────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
                    ┌───────────────┐
                    │   LMStudio    │
                    │  (localhost)  │
                    │   Port: 1234  │
                    └───────────────┘
```

## Key Design Patterns

### 1. Orchestrator Pattern
- `ResearchOrchestrator` coordinates all components
- Manages lifecycle and dependencies
- Handles errors and cleanup

### 2. Worker Pool Pattern
- Multiple agents work in parallel
- Results aggregated by orchestrator
- Fault-tolerant (failed workers don't stop others)

### 3. Version Control Pattern
- Incremental versioning (0001, 0002, etc.)
- Each version is immutable
- Easy to track evolution

### 4. RAG Pattern
- Documents chunked and stored in vector DB
- Context retrieved during refinement
- Knowledge accumulates over time

### 5. Graceful Shutdown Pattern
- Signal handlers for Ctrl+C
- Resources cleaned up properly
- State saved before exit

## Extension Points

### Add New Agent Types
Edit `agents/` to add specialized agents:
- `citation_agent.py`: Add citations
- `fact_checker_agent.py`: Verify facts
- `summary_agent.py`: Generate summaries

### Add New Storage Backends
Edit `storage/vector_store.py`:
- Add `_init_chromadb()` for ChromaDB
- Add `_init_pinecone()` for Pinecone
- Add `_init_weaviate()` for Weaviate

### Add New Refinement Strategies
Edit `refinement/refiner.py`:
- Quality-based: Only refine if quality improves
- Targeted: Focus on specific sections
- Collaborative: Multiple agents refine different parts

### Add Web Search
Create `agents/search_agent.py`:
- Integrate DuckDuckGo
- Add web scraping
- Incorporate external sources

## Performance Considerations

### Bottlenecks
1. **LMStudio inference**: Depends on model size and hardware
2. **Vector search**: SQLite is fast enough for local use
3. **File I/O**: Async operations prevent blocking
4. **Worker parallelism**: Limited by LMStudio throughput

### Optimization Tips
1. Use GPU acceleration in LMStudio
2. Reduce `num_workers` if system is overloaded
3. Use smaller models (7B instead of 13B)
4. Increase `chunk_size` to reduce DB operations
5. Enable caching in Agno agents

## Testing Strategy

### Unit Tests (Future)
- Test each module independently
- Mock LMStudio responses
- Verify file operations
- Check vector storage

### Integration Tests (Future)
- Test full workflow
- Verify agent coordination
- Check data persistence
- Validate error handling

### Manual Testing
```bash
# Test basic functionality
python research_orchestrator.py "test topic"

# Test with minimal config
python research_orchestrator.py "quick test" --workers 2

# Test interruption
python research_orchestrator.py "test"
# Then press Ctrl+C after 30 seconds
```

## Deployment Options

### Local Development
- Current setup (recommended for development)

### Docker Container
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "research_orchestrator.py"]
```

### Cloud Deployment
- Package as Python application
- Use cloud LLM instead of LMStudio
- Replace SQLite with PostgreSQL + pgvector
- Add FastAPI for web interface

---

For more information, see:
- [README.md](README.md) - User documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
