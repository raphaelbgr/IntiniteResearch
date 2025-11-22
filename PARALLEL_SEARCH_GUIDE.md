# Parallel DuckDuckGo Search Guide

## Overview

The Infinite Research system uses a **single powerful agent** with **parallel DuckDuckGo search capabilities** that can execute 1-10 web searches simultaneously.

This approach is more efficient than running multiple worker agents, as:
- ✅ The AI decides which searches to run in parallel
- ✅ One agent with deep context vs multiple shallow agents
- ✅ Automatic query optimization by the AI
- ✅ Better token utilization
- ✅ More coherent research synthesis

## Architecture

```
User Prompt
    ↓
Single Research Agent (with LMStudio)
    ↓
┌──────────────────────────────────────┐
│  Parallel Search Tool                │
│  (1-10 queries simultaneously)       │
│                                      │
│  Query 1: "topic basics"     ──→ DDG│
│  Query 2: "topic applications" →  DDG│
│  Query 3: "topic challenges"  ─→  DDG│
│  Query 4: "topic future"      ──→ DDG│
│  Query 5: "topic history"     ──→ DDG│
│  ...                                 │
└──────────────────────────────────────┘
    ↓
Aggregated Results
    ↓
AI Synthesis
    ↓
Comprehensive Research Document
```

## How It Works

### 1. AI Decides Search Queries

The agent is instructed to break down research topics into multiple aspects:

```python
# Example: Researching "quantum computing"
queries = [
    "quantum computing basics principles",
    "quantum algorithms NISQ era",
    "quantum hardware qubit technology",
    "quantum computing applications industry",
    "quantum computing challenges limitations",
    "quantum computing future prospects"
]
```

### 2. Parallel Execution

The tool executes all searches simultaneously using asyncio:

```python
# Internal implementation
results = await asyncio.gather(
    search("query 1"),
    search("query 2"),
    search("query 3"),
    ...
)
```

### 3. Result Aggregation

Results are returned in a structured format:

```json
{
  "total_queries": 5,
  "successful_queries": 5,
  "total_results": 25,
  "queries": [
    {
      "query": "quantum computing basics",
      "status": "success",
      "result_count": 5,
      "results": [
        {
          "title": "Introduction to Quantum Computing",
          "url": "https://...",
          "body": "..."
        },
        ...
      ]
    },
    ...
  ]
}
```

### 4. AI Synthesis

The agent then:
- Cross-references information across all searches
- Identifies key themes and patterns
- Synthesizes into a coherent document
- Adds analysis and insights

## Tool Usage by AI

### The Agent's Instructions

The agent is given clear instructions:

```markdown
**Your Capabilities:**
- You have access to parallel web search tools that can search 1-10 different queries simultaneously
- Use the parallel_search tool to gather information from multiple angles

**Research Guidelines:**
1. **Multi-angle Research**: Break topics down into 3-7 key aspects
2. **Parallel Searching**: Use parallel_search with multiple related queries
3. **Deep Analysis**: Cross-reference and synthesize findings
```

### Example Tool Call

When researching, the AI agent will call:

```python
parallel_search(
    search_queries=[
        "AI ethics principles guidelines",
        "AI bias fairness machine learning",
        "AI regulation policy frameworks",
        "AI safety alignment research",
        "AI transparency explainability"
    ]
)
```

## Benefits Over Multiple Workers

| Aspect | Multiple Workers | Single Agent with Parallel Search |
|--------|------------------|-----------------------------------|
| **Context** | Shallow per worker | Deep, unified context |
| **Coordination** | Manual aggregation | AI-driven synthesis |
| **Query Quality** | Fixed decomposition | Dynamic, intelligent queries |
| **Token Usage** | High (multiple agents) | Optimized (one agent) |
| **Coherence** | Requires merging | Naturally coherent |
| **Flexibility** | Static 5 workers | Dynamic 1-10 queries |

## Configuration

### config.yaml

```yaml
research:
  parallel_search_enabled: true
  refinement_delay: 10
  output_dir: "./generation"
```

### Search Tool Parameters

In `agents/research_agent.py`:

```python
parallel_search = ParallelDuckDuckGoSearch(
    search=True,              # Enable text search
    news=True,                # Enable news search
    max_results_per_query=5,  # Results per query
    timeout=10                # Timeout seconds
)
```

## Usage Examples

### Basic Research

```bash
python research_orchestrator.py "Impact of climate change on agriculture"
```

The agent will automatically:
1. Break down the topic into aspects (impacts, adaptation, technology, policy, etc.)
2. Execute 5-7 parallel searches
3. Gather 25-35 web results
4. Synthesize into comprehensive document

### Refinement Loop

During refinement, the agent can:
- Search for recent developments
- Fill in gaps from previous versions
- Update with latest information
- Add depth to specific sections

## Advanced Features

### 1. News Search

The agent can also search news in parallel:

```python
parallel_news_search(
    search_queries=[
        "AI regulation news 2025",
        "machine learning breakthroughs",
        "AI ethics concerns recent"
    ]
)
```

### 2. Mixed Search Strategies

The agent intelligently decides:
- When to use text search vs news search
- How many queries to run (1-10)
- What level of detail needed per query

### 3. Iterative Deepening

During refinement:
- First refinement: Broad searches
- Later refinements: Targeted, specific searches
- Fills in gaps incrementally

## Performance

### Typical Research Session

```
Initial Research:
  - 6 parallel searches
  - ~30 web results
  - ~3-5 minutes
  - Document: 2000-3000 words

First Refinement:
  - 4 parallel searches (filling gaps)
  - ~20 web results
  - ~2-3 minutes
  - Document: 3000-4000 words

Nth Refinement:
  - 2-3 targeted searches
  - ~10-15 web results
  - ~1-2 minutes
  - Document: Incremental improvements
```

### Resource Usage

- **Network**: 1-10 concurrent DDG requests
- **LMStudio**: Single agent inference
- **Memory**: Minimal (no worker pool overhead)
- **Tokens**: Optimized (one context, not five)

## Debugging

### Enable Tool Call Logging

In `agents/research_agent.py`:

```python
agent = Agent(
    ...
    show_tool_calls=True,  # See search queries in real-time
    ...
)
```

### Check Search Results

Logs will show:

```
[INFO] Executing 6 parallel searches with 5 results each
[INFO] Query 1: "quantum computing basics" - 5 results
[INFO] Query 2: "quantum algorithms" - 5 results
...
[INFO] Total: 30 results from 6 queries
```

## Limitations

1. **DuckDuckGo Rate Limits**: Don't exceed 10 parallel queries
2. **Result Quality**: DDG results may vary in quality
3. **Timeout**: Each search limited to 10 seconds
4. **Context Length**: AI must process all results in context

## Future Enhancements

- [ ] **Semantic search**: Use embeddings to find most relevant results
- [ ] **Source validation**: Verify source authority
- [ ] **Citation tracking**: Automatic reference management
- [ ] **Search caching**: Avoid redundant searches
- [ ] **Multi-engine**: Add Bing, Google alternative search
- [ ] **Content extraction**: Automatically fetch and parse web pages

## Tips for Best Results

1. **Let the AI decide**: Don't force specific queries, let the agent determine them
2. **Broad topics first**: Start with general searches, refine later
3. **Monitor logs**: Check which searches the AI is running
4. **Adjust parameters**: Tune `max_results_per_query` based on needs
5. **Use refinement**: Let the system iteratively improve over multiple passes

## Troubleshooting

### "Too many parallel searches" error

```
Error: Maximum 10 parallel searches allowed
```

**Solution**: The AI tried more than 10 queries. This is hard-limited in the tool.

### Slow searches

**Solution**:
- Reduce `timeout` parameter
- Reduce `max_results_per_query`
- Check network connection

### Poor quality results

**Solution**:
- Refine search queries (AI learns this over refinements)
- Increase `max_results_per_query` for more options
- Use news search for recent topics

---

**This architecture gives your AI agent superpowers while keeping the system simple and efficient!** 🚀
