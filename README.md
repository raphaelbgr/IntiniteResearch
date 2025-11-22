# Infinite Research Refinement System

An autonomous research system using Agno agents with RAG capabilities and **parallel DuckDuckGo search (1-10 queries)** to conduct deep web research, continuously refining documents until manually interrupted.

## Features

- **Local LLM Integration**: Connects to LMStudio for privacy and local execution
- **Parallel Web Search**: Agent can execute 1-10 DuckDuckGo searches simultaneously
- **AI-Driven Research**: Single intelligent agent decides what to search and how
- **Input File Support**: Include your own files (PDFs, texts, data) as research context
- **Optimized for Weak Models**: Only uses last 2 refinements + KB/RAG for minimal context
- **Iterative Learning**: Search terms evolve and improve each iteration
- **Infinite Refinement Loop**: Continuously improves documents until interrupted
- **Version Control**: Every refinement is saved with incremental versioning + search terms
- **Gap Detection**: Automatically identifies weak sections to improve
- **Vector Database & RAG**: Stores document embeddings for context-aware refinement
- **File-based SQL Storage**: SQLite for efficient local data management
- **Graceful Shutdown**: Safely handles Ctrl+C interruptions

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md), [PARALLEL_SEARCH_GUIDE.md](PARALLEL_SEARCH_GUIDE.md), and [WEAK_MODEL_OPTIMIZATION.md](WEAK_MODEL_OPTIMIZATION.md) for detailed system design.

```
User Prompt + Input Files → LMStudio ← Agno Agent (Parallel Search)
                                ↓              ↓
                         1-10 Parallel DuckDuckGo Searches
                                ↓              ↓
                         AI Synthesis → refinement-0001.md
                                ↓
                    ┌───────────┴────────────┐
                    │ Refinement Loop        │
                    │ (Infinite)             │
                    │                        │
                    │ Context per iteration: │
                    │ • Last 2 refinements   │
                    │ • Input files          │
                    │ • KB/RAG (top 3)       │
                    │ • Search terms (prev)  │
                    │ • Identified gaps      │
                    └───────────┬────────────┘
                                ↓
                    refinement-NNNN.md (with learned search terms)
```

## Requirements

- Python 3.10+
- LMStudio running on localhost (or remote server)
- A loaded model in LMStudio

## Installation

### 1. Clone or setup the project

```bash
cd InfiniteResearch
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure LMStudio

1. Open LMStudio
2. Load your preferred model
3. Start the local server (usually runs on `http://localhost:1234`)
4. Note your model name from LMStudio

### 5. Update configuration

Edit `config.yaml` and update:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"  # Your LMStudio URL
  model: "your-model-name"  # Model name from LMStudio
```

## Usage

### Basic Usage

```bash
python research_orchestrator.py "Your research topic here"
```

### Example

```bash
python research_orchestrator.py "The impact of quantum computing on cryptography"
```

### What Happens

1. **Initialization**: Creates a unique research session with ID `research-YYYYMMDD-HHMMSS`
2. **AI-Driven Research**: Agent breaks topic into aspects and executes parallel web searches
   - AI decides: "I need to search for X, Y, Z aspects"
   - Tool executes 1-10 DuckDuckGo searches simultaneously
   - AI synthesizes results into comprehensive document
3. **Initial Document**: Creates `refinement-0001.md` with research findings
4. **Infinite Refinement**: Continuously improves the document:
   - Searches for new information
   - Fills in gaps from previous versions
   - Adds depth and clarity
   - `refinement-0002.md`, `0003.md`, `0004.md`...
   - ... (continues until you press Ctrl+C)

### Stopping the Process

Press **Ctrl+C** to gracefully stop the refinement loop. Your work is automatically saved.

## Output Structure

```
/generation/
  └── research-20250121-143022/
      ├── refinement-0001.md       # Initial research
      ├── refinement-0002.md       # First refinement
      ├── refinement-0003.md       # Second refinement
      ├── refinement-NNNN.md       # Latest version
      ├── rag/
      │   └── vectors.db           # Vector embeddings
      ├── kb/
      │   ├── knowledge.db         # Knowledge base
      │   ├── knowledge.txt        # Text knowledge
      │   └── metadata.json        # Research metadata
      ├── memory/
      │   └── agent_memory.db      # Agent conversation history
      └── logs/
          └── research.log         # Detailed logs
```

## Configuration

Edit `config.yaml` to customize:

### LMStudio Settings

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"  # LMStudio server URL
  model: "local-model"                   # Model name
  temperature: 0.7                       # Creativity (0.0-1.0)
  max_tokens: 4096                       # Max response length
```

### Research Settings

```yaml
research:
  parallel_search_enabled: true  # Enable parallel DuckDuckGo search
  refinement_delay: 10           # Seconds between refinements
  output_dir: "./generation"
  max_refinements: null          # null = infinite, or set a number
```

### Vector Database

```yaml
vector_db:
  type: "sqlite"  # Options: "sqlite", "pgvector"
  chunk_size: 512
  chunk_overlap: 50
```

### Logging

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "research.log"
  console: true
```

## Advanced Usage

### Resume Research

To manually refine a specific version:

```python
from storage.file_manager import FileManager
from refinement.refiner import RefinementEngine

# Load existing research
fm = FileManager()
research_id = "research-20250121-143022"

# Continue refinement from version 5
# ... (requires manual setup of components)
```

### Query Vector Database

Search previous research:

```python
from storage.vector_store import VectorStore
from pathlib import Path

vs = VectorStore(
    research_id="research-20250121-143022",
    base_dir=Path("generation/research-20250121-143022"),
    db_type="sqlite"
)

# Search for relevant chunks
results = vs.search_similar("quantum algorithms", limit=5)
for result in results:
    print(result['content'])
```

### Custom Search Parameters

Adjust search behavior in `agents/research_agent.py`:

```python
parallel_search = ParallelDuckDuckGoSearch(
    search=True,
    news=True,
    max_results_per_query=5,  # Results per search
    timeout=10                # Timeout per search
)
```

**Note**: Agent decides how many searches (1-10) based on the research task.

## Troubleshooting

### LMStudio Connection Error

```
Error: Connection refused to http://localhost:1234
```

**Solution**:
1. Ensure LMStudio is running
2. Check the server is started in LMStudio
3. Verify the port in `config.yaml` matches LMStudio

### Model Not Found

```
Error: Model 'local-model' not found
```

**Solution**:
1. Open LMStudio
2. Check your loaded model name
3. Update `config.yaml` with the exact model name

### Slow Refinements

**Solution**:
1. Reduce `max_tokens` in config
2. Reduce `num_workers`
3. Increase `refinement_delay`
4. Use a smaller/faster model in LMStudio

### Memory Issues

**Solution**:
1. Reduce `num_workers`
2. Close other applications
3. Use a smaller model
4. Increase system RAM

## How It Works

### 1. Initial Research Phase

The AI agent analyzes your topic and determines key aspects to research:
- Overview and fundamentals
- Historical background
- Current developments
- Applications and use cases
- Challenges and limitations
- Future trends and implications

The agent then executes 5-7 parallel web searches (one per aspect).

### 2. Synthesis

Search results are analyzed by the AI and synthesized into a comprehensive, coherent document.

### 3. Refinement Loop

```python
while not interrupted:
    1. Load previous version
    2. Query vector DB for context
    3. Agent analyzes and improves
    4. Save new version
    5. Store in vector DB
    6. Update knowledge base
    7. Wait (refinement_delay)
    8. Repeat
```

### 4. Vector Storage

Each version is:
- Split into chunks (paragraphs)
- Stored in SQLite vector database
- Available for future context retrieval

This builds a knowledge base specific to your research topic.

## Extending the System

### Add Custom Tools

Modify `agents/research_agent.py` to add Agno tools:

```python
from agno.tools import DuckDuckGo, Newspaper4k

# Add tools to agent
self.agent.tools = [DuckDuckGo(), Newspaper4k()]
```

### Use PgVector Instead of SQLite

1. Install PostgreSQL with pgvector extension
2. Update `config.yaml`:

```yaml
vector_db:
  type: "pgvector"
  pgvector:
    host: "localhost"
    port: 5432
    database: "research_db"
    user: "postgres"
    password: "yourpassword"
```

### Custom Refinement Strategy

Edit `refinement/refiner.py` to customize refinement prompts and logic.

### Add Web Search

Install and configure web search tools:

```bash
pip install agno[duckduckgo]
```

Then add to your agent in `agents/research_agent.py`.

## Performance Tips

1. **Use GPU acceleration** in LMStudio for faster inference
2. **Adjust worker count** based on your CPU/GPU capacity
3. **Increase refinement delay** if your system is struggling
4. **Use smaller models** (7B-13B) for faster iterations
5. **Monitor system resources** during execution

## FAQ

**Q: Can I use a remote LMStudio server?**
A: Yes! Update `base_url` in config to point to your remote server.

**Q: Does this work with other LLM providers?**
A: Yes! Agno supports 25+ providers. Modify the model configuration in `agents/research_agent.py`.

**Q: How do I stop infinite refinement?**
A: Press Ctrl+C. The system will gracefully save and exit.

**Q: Can I limit the number of refinements?**
A: Yes! Set `max_refinements` in `config.yaml` to a specific number.

**Q: Where are the embeddings generated?**
A: Currently, the system stores text chunks without embeddings. To add embeddings, integrate `sentence-transformers` or use LMStudio's embedding API.

**Q: Can I run multiple research sessions simultaneously?**
A: Yes! Each session gets a unique ID and directory. Run multiple terminals with different topics.

## Contributing

Feel free to extend and customize this system for your needs!

## License

This project is provided as-is for educational and research purposes.

## Credits

Built with:
- [Agno](https://github.com/agno-agi/agno) - Multi-agent framework
- [LMStudio](https://lmstudio.ai) - Local LLM runtime
- Python asyncio for parallel processing

---

**Happy Researching!** 🔬📚✨
