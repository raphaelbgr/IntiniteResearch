# Changelog

## Version 2.0 - Parallel Search Architecture (Current)

### Major Changes

**Replaced multiple workers with single intelligent agent + parallel search**

#### Architecture Changes
- ❌ Removed: 5-worker pool system
- ✅ Added: Single agent with parallel DuckDuckGo search tool (1-10 queries)
- ✅ Added: AI-driven query generation
- ✅ Added: Parallel asyncio-based web search execution

#### Benefits
- **Better context**: Single agent maintains deep context vs. shallow worker context
- **Smarter queries**: AI decides what to search based on topic analysis
- **More efficient**: One agent call vs. five worker calls + aggregation
- **Flexible**: 1-10 searches dynamically chosen vs. fixed 5 workers
- **Cleaner code**: Simpler architecture, easier to maintain

#### New Files
- `tools/parallel_search.py` - Parallel DuckDuckGo search tool
- `tools/__init__.py` - Tools module
- `PARALLEL_SEARCH_GUIDE.md` - Comprehensive guide to parallel search
- `CHANGELOG.md` - This file

#### Modified Files
- `agents/research_agent.py` - Now includes parallel search tool
- `research_orchestrator.py` - Simplified to use single agent
- `config.yaml` - Updated configuration format
- `requirements.txt` - Added duckduckgo-search dependency
- `README.md` - Updated documentation

#### Deprecated
- `agents/worker_pool.py` - No longer used (kept for reference)

### How to Upgrade from v1.0

1. **Install new dependency**:
   ```bash
   pip install duckduckgo-search>=6.0.0
   ```

2. **Update config.yaml**:
   ```yaml
   # Old (v1.0)
   research:
     num_workers: 5

   # New (v2.0)
   research:
     parallel_search_enabled: true
   ```

3. **Run as usual**:
   ```bash
   python research_orchestrator.py "Your topic"
   ```

### Technical Details

#### Parallel Search Tool API

```python
parallel_search(
    search_queries: List[str],  # 1-10 queries
    max_results: Optional[int] = 5
) -> str  # JSON with aggregated results
```

#### Agent Instructions

Agent is now instructed to:
- Break topics into 3-7 key aspects
- Use parallel_search with multiple related queries
- Cross-reference and synthesize results
- Use 1-10 searches based on task complexity

#### Example Tool Call

```python
# AI agent calls:
parallel_search(search_queries=[
    "quantum computing basics",
    "quantum algorithms",
    "quantum hardware",
    "quantum applications",
    "quantum challenges"
])

# Returns aggregated results from 5 parallel searches
```

### Performance Comparison

| Metric | v1.0 (5 Workers) | v2.0 (Parallel Search) |
|--------|------------------|------------------------|
| **Agent calls** | 5 (workers) + 1 (main) | 1 |
| **Context depth** | Shallow per worker | Deep, unified |
| **Query flexibility** | Fixed decomposition | AI-driven, dynamic |
| **Token usage** | High (6 agents) | Optimized (1 agent) |
| **Coherence** | Requires aggregation | Naturally coherent |
| **Setup complexity** | Worker pool + coordination | Single agent + tool |

### Migration Guide

#### Before (v1.0)

```python
# Old: Multiple workers research subtopics
worker_pool = WorkerPool(num_workers=5, ...)
results = await worker_pool.research_parallel(topic)
doc = worker_pool.aggregate_results(results)
```

#### After (v2.0)

```python
# New: Single agent with parallel search tool
agent = ResearchAgent(...)  # Has parallel search tool
doc = await agent.research(topic)  # AI uses tool automatically
```

### Breaking Changes

None - External API remains the same:
```bash
python research_orchestrator.py "Your topic"
```

### Bug Fixes

- Fixed: Worker coordination overhead
- Fixed: Context fragmentation across workers
- Fixed: Inconsistent worker output formats
- Improved: Error handling in parallel operations

### Known Issues

- DuckDuckGo rate limiting may affect >10 parallel searches
- Timeout set to 10s per search (configurable)
- News search may return fewer results than text search

---

## Version 1.0 - Initial Release

### Features

- Multi-worker parallel research system
- 5 workers researching different subtopics
- LMStudio integration
- Vector database with RAG
- Infinite refinement loop
- SQLite storage
- File-based research organization

### Architecture

- `WorkerPool` managing 5 research workers
- Manual topic decomposition
- Worker result aggregation
- Single refinement agent

### Files

- Initial project structure
- Core modules (agents, storage, refinement, utils)
- Documentation (README, ARCHITECTURE, QUICKSTART)
- Configuration and requirements

---

## Future Roadmap

### v2.1 (Planned)
- [ ] MCP server integration for search
- [ ] Semantic result filtering with embeddings
- [ ] Automatic citation management
- [ ] Search result caching
- [ ] Quality scoring for search results

### v2.2 (Planned)
- [ ] Multi-search engine support (Bing, Brave)
- [ ] Web page content extraction and parsing
- [ ] Automatic fact-checking
- [ ] Source credibility assessment

### v3.0 (Future)
- [ ] Multi-document output (split by topics)
- [ ] Collaborative multi-user research
- [ ] Web UI for monitoring
- [ ] Real-time streaming of refinements
- [ ] Custom tool integration framework
