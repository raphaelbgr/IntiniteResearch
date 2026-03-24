# Quick Reference Guide

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml`:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  model: "your-model-name"  # ← Change this

research:
  parallel_search_enabled: true
  refinement_delay: 10
```

## Basic Usage

```bash
# Start research
python research_orchestrator.py "Your research topic"

# Stop (press Ctrl+C when satisfied)
```

## File Structure

```
generation/
  └── research-YYYYMMDD-HHMMSS/
      ├── refinement-0001.md  ← Initial research
      ├── refinement-0002.md  ← First refinement
      ├── refinement-NNNN.md  ← Latest version
      ├── rag/vectors.db      ← Vector embeddings
      ├── kb/knowledge.db     ← Knowledge base
      └── memory/             ← Agent memory
```

## How It Works

```
1. You: "Research topic"
   ↓
2. AI Agent analyzes topic
   ↓
3. AI decides: "I need to search for X, Y, Z"
   ↓
4. Tool: Executes 5-7 parallel DuckDuckGo searches
   ↓
5. AI: Synthesizes results → refinement-0001.md
   ↓
6. Loop: AI refines infinitely
   - Searches for new info
   - Fills gaps
   - Improves clarity
   - Saves refinement-NNNN.md
   ↓
7. You: Press Ctrl+C to stop
```

## Parallel Search Tool

### What AI Agent Can Do

```python
# AI agent has access to:
parallel_search(search_queries=[
    "query 1",
    "query 2",
    ...
    "query 10"  # Max 10 parallel searches
])
```

### AI Instructions

Agent is told:
- Break topics into 3-7 key aspects
- Use 1-10 parallel searches
- Cross-reference multiple sources
- Synthesize into coherent documents

### Example AI Decision

```
Topic: "Quantum Computing"

AI thinks:
"I should search for:
1. Basics and principles
2. Current hardware state
3. Algorithms (NISQ era)
4. Industry applications
5. Technical challenges
6. Future prospects"

→ Executes 6 parallel searches
→ Gets ~30 web results
→ Synthesizes into document
```

## Key Files

| File | Purpose |
|------|---------|
| `research_orchestrator.py` | Main entry point |
| `config.yaml` | Configuration |
| `agents/research_agent.py` | AI agent with search tool |
| `tools/parallel_search.py` | Parallel search implementation |
| `refinement/refiner.py` | Refinement engine |
| `storage/file_manager.py` | File operations |
| `storage/vector_store.py` | Vector database |

## Configuration Options

### LMStudio

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  api_key: "lm-studio"  # Dummy key
  model: "llama-3.1-8b-instruct"
  temperature: 0.7      # 0.0 = deterministic, 1.0 = creative
  max_tokens: 4096      # Max response length
```

### Research

```yaml
research:
  parallel_search_enabled: true
  refinement_delay: 10  # Seconds between refinements
  output_dir: "./generation"
  max_refinements: null  # null = infinite, or set number
```

### Search Tool

In `agents/research_agent.py`:

```python
parallel_search = ParallelDuckDuckGoSearch(
    search=True,              # Enable text search
    news=True,                # Enable news search
    max_results_per_query=5,  # Results per query
    timeout=10                # Timeout per search
)
```

## Common Commands

```bash
# Basic research
python research_orchestrator.py "AI ethics"

# List research sessions
ls generation/

# View latest version
cat generation/research-*/refinement-*.md | tail -1

# Run examples
python example_usage.py
```

## Troubleshooting

### Can't connect to LMStudio

1. Check LMStudio is running
2. Check server is started (port 1234)
3. Verify model is loaded
4. Check `base_url` in config.yaml

### Model not found

1. Open LMStudio
2. Note exact model name
3. Update `model` in config.yaml

### Slow performance

1. Use smaller model (7B vs 13B)
2. Increase `refinement_delay`
3. Reduce `max_results_per_query`
4. Enable GPU in LMStudio

### Search failing

1. Check internet connection
2. Verify `duckduckgo-search` installed
3. Check DuckDuckGo accessible
4. Try reducing parallel searches

## Advanced Usage

### Programmatic Usage

```python
from research_orchestrator import ResearchOrchestrator

orchestrator = ResearchOrchestrator()
await orchestrator.run("Your topic")
```

### Custom Search Parameters

Edit `agents/research_agent.py`:

```python
parallel_search = ParallelDuckDuckGoSearch(
    max_results_per_query=10,  # More results
    timeout=20                 # Longer timeout
)
```

### Resume Research

```python
from storage.file_manager import FileManager

fm = FileManager()
sessions = fm.list_research_sessions()
print(sessions)  # Pick one to continue
```

## Performance Tips

1. **GPU Acceleration**: Enable in LMStudio
2. **Model Size**: 7B-13B models are fastest
3. **Refinement Delay**: Increase if system is slow
4. **Search Results**: Reduce if too much data
5. **Monitor Resources**: Watch CPU/RAM usage

## Keyboard Shortcuts

- **Ctrl+C**: Stop refinement loop (graceful)
- **Ctrl+Z**: Pause process
- **Ctrl+\\**: Force quit (not recommended)

## Documentation

- [README.md](README.md) - Full documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [PARALLEL_SEARCH_GUIDE.md](PARALLEL_SEARCH_GUIDE.md) - Search tool details
- [QUICKSTART.md](QUICKSTART.md) - Getting started
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code organization
- [CHANGELOG.md](CHANGELOG.md) - Version history

## Support

- Check documentation
- Review examples in `example_usage.py`
- Check Agno docs: https://docs.agno.com
- Check DuckDuckGo search: https://pypi.org/project/duckduckgo-search/

## Example Topics

```bash
# Technology
python research_orchestrator.py "Large language models in 2025"

# Science
python research_orchestrator.py "CRISPR gene editing applications"

# Business
python research_orchestrator.py "Remote work productivity trends"

# Current events (uses news search)
python research_orchestrator.py "Latest developments in AI regulation"
```

---

**Happy Researching!** 🚀
