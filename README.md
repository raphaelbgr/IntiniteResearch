# Infinite Research Refinement System

An autonomous research system using Agno agents with RAG capabilities and **parallel DuckDuckGo search (1-10 queries)** to conduct deep web research, continuously refining documents until manually interrupted.

## Features

- **Local LLM Integration** - Connects to LMStudio for privacy and local execution
- **Parallel Web Search** - Agent executes 1-10 DuckDuckGo searches simultaneously
- **AI-Driven Research** - Single intelligent agent decides what to search and how
- **Input File Support** - Include your own files (PDFs, texts, data) as research context
- **Optimized for Weak Models** - Only uses last 2 refinements + KB/RAG for minimal context
- **Self-Evolving Search Terms** - Search strategy improves each iteration based on results
- **Self-Evaluation Loop** - Every 10 iterations, the agent scores its own progress and identifies gaps
- **Infinite Refinement Loop** - Continuously improves documents until interrupted (Ctrl+C)
- **Version Control** - Every refinement saved with incremental versioning
- **Vector Database & RAG** - SQLite or PgVector for context-aware refinement

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) and the [docs/](docs/) folder for detailed system design.

```
User Prompt + Input Files -> LMStudio <- Agno Agent (Parallel Search)
                                |              |
                         1-10 Parallel DuckDuckGo Searches
                                |              |
                         AI Synthesis -> refinement-0001.md
                                |
                    +-----------+------------+
                    | Refinement Loop        |
                    | (Infinite)             |
                    |                        |
                    | Context per iteration: |
                    | - Last 2 refinements   |
                    | - Input files          |
                    | - KB/RAG (top 3)       |
                    | - Search terms (prev)  |
                    | - Identified gaps       |
                    +-----------+------------+
                                |
                    refinement-NNNN.md (with learned search terms)
```

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/raphaelbgr/IntiniteResearch.git
cd IntiniteResearch
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure LMStudio
#    - Open LMStudio, load a model, start the server (http://localhost:1234)
#    - Edit config.yaml with your model name

# 4. Run
python research_orchestrator.py "Your research topic here"
```

### Example

```bash
python research_orchestrator.py "The impact of quantum computing on cryptography"
```

Press **Ctrl+C** to gracefully stop. Your work is automatically saved.

## How It Works

1. **Initial Research** - Agent analyzes your topic, executes 5-7 parallel web searches, synthesizes results into `refinement-0001.md`
2. **Refinement Loop** - Each iteration: load previous version, query vector DB for context, agent improves the document, save new version, store in vector DB
3. **Self-Evaluation** (every 10 iterations) - Scores progress on objective alignment, completeness, and input alignment. Identifies gaps and generates recommendations
4. **Search Evolution** - Search terms get more targeted each iteration based on what the agent learned

## Output Structure

```
generation/
  research-YYYYMMDD-HHMMSS/
    refinement-0001.md       # Initial research
    refinement-0002.md       # First refinement
    refinement-NNNN.md       # Latest version
    report/
      report-0001.md         # Evaluation at iteration 10
      report-0002.md         # Evaluation at iteration 20
    rag/
      vectors.db             # Vector embeddings
    kb/
      knowledge.db           # Knowledge base
      metadata.json          # Research metadata
    logs/
      research.log
```

## Configuration

Edit `config.yaml`:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  model: "your-model-name"
  temperature: 0.7
  max_tokens: 4096

research:
  parallel_search_enabled: true
  refinement_delay: 10           # Seconds between iterations
  max_refinements: null          # null = infinite
  enable_evaluation: true        # Self-evaluation reports
  evaluation_frequency: 10       # Evaluate every N iterations

vector_db:
  type: "sqlite"                 # or "pgvector"
```

## Project Structure

```
.
+-- research_orchestrator.py   # Main entry point
+-- config.yaml                # Configuration
+-- agents/                    # Agent implementations
|   +-- research_agent.py      # Main research agent
|   +-- agent0_orchestrator.py # Self-evolving agent system
|   +-- bmad_orchestrator.py   # Multi-agent coordinator
|   +-- worker_pool.py         # Parallel worker management
+-- refinement/                # Refinement engine
|   +-- refiner.py             # Iterative document improvement
|   +-- evaluator.py           # Self-evaluation and scoring
|   +-- compiler.py            # Document compilation
+-- storage/                   # Data persistence
|   +-- file_manager.py        # File I/O and versioning
|   +-- vector_store.py        # SQLite/PgVector storage
|   +-- source_kb.py           # Knowledge base
+-- tools/                     # Search tools
|   +-- parallel_ddg.py        # Parallel DuckDuckGo search
+-- utils/                     # Utilities
|   +-- config_loader.py       # YAML config loading
|   +-- context_manager.py     # Context window management
|   +-- source_tracker.py      # Source URL tracking
+-- models/                    # Data models
+-- tests/                     # Test suite (52 tests)
+-- docs/                      # Detailed documentation
+-- input/                     # Place input files here
```

## Documentation

Detailed docs in the [docs/](docs/) folder:

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design overview
- [docs/ITERATION_FLOW.md](docs/ITERATION_FLOW.md) - How the iteration cycle works
- [docs/EVALUATION_FEATURE.md](docs/EVALUATION_FEATURE.md) - Self-evaluation mechanism
- [docs/PARALLEL_SEARCH_GUIDE.md](docs/PARALLEL_SEARCH_GUIDE.md) - Parallel search implementation
- [docs/WEAK_MODEL_OPTIMIZATION.md](docs/WEAK_MODEL_OPTIMIZATION.md) - Context optimization for small models
- [docs/AGENT0_INTEGRATION.md](docs/AGENT0_INTEGRATION.md) - Agent0 self-evolving system
- [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) - Windows-specific setup

## Requirements

- Python 3.10+
- LMStudio (or any OpenAI-compatible API)
- A loaded model in LMStudio

## Built With

- [Agno](https://github.com/agno-agi/agno) - Multi-agent framework
- [LMStudio](https://lmstudio.ai) - Local LLM runtime

## License

This project is provided as-is for educational and research purposes.
