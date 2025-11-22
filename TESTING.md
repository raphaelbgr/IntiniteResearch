# Testing Guide

Complete guide to testing the Infinite Research system.

## Step 1: Setup Test (No LMStudio Required)

This verifies all dependencies and imports work.

```bash
python test_setup.py
```

**What it tests:**
- ✓ All dependencies installed (agno, openai, ddgs, etc.)
- ✓ Project imports work
- ✓ config.yaml is valid

**Expected output:**
```
Testing imports...
✓ agno (installed)
✓ openai (1.x.x)
✓ duckduckgo-search (ddgs)
✓ pydantic (2.x.x)
...

Test Summary
Dependencies         ✓ PASS
Project Imports      ✓ PASS
Configuration        ✓ PASS

✓ All tests passed! System is ready.
```

**If it fails:**
```bash
pip install -r requirements.txt
```

---

## Step 2: Parallel Search Test (No LMStudio Required)

This tests the DuckDuckGo search tool directly.

```bash
python test_parallel_search.py
```

**What it tests:**
- ✓ Single search query works
- ✓ Multiple parallel searches work
- ✓ News search works
- ✓ Error handling (too many queries, empty list)
- ✓ Source deduplication

**Expected output:**
```
Test 1: Single Search Query
Total queries: 1
Successful: 1
Total results: 3
Unique sources: 3

First source:
  Title: Python Tutorial
  URL: https://...
  Snippet: ...

Test 2: Multiple Parallel Searches (3 queries)
Total queries: 3
Successful: 3
Total results: 6
Unique sources: 6

...

✓ All tests completed!
```

**This proves the search tool works independently!**

---

## Step 3: LMStudio Setup

### 3.1 Start LMStudio

1. Open LMStudio
2. Load a model (e.g., `llama-3.1-8b-instruct`)
3. Click "Start Server"
4. Verify it's running on `http://localhost:1234`

### 3.2 Configure

Edit `config.yaml`:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  model: "llama-3.1-8b-instruct"  # ← Your exact model name
  temperature: 0.7
  max_tokens: 2048  # Start small for testing
```

**Get exact model name:**
- Check LMStudio's loaded model name
- Must match exactly!

### 3.3 Test LMStudio Connection

```bash
python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:1234/v1', api_key='lm-studio')
response = client.chat.completions.create(
    model='llama-3.1-8b-instruct',  # Your model name
    messages=[{'role': 'user', 'content': 'Say hello'}],
    max_tokens=50
)
print('✓ LMStudio connected!')
print(f'Response: {response.choices[0].message.content}')
"
```

**Expected:** Should print "✓ LMStudio connected!" and a response.

**If it fails:**
- Check LMStudio server is running
- Check port (default: 1234)
- Check model name matches exactly

---

## Step 4: Quick Research Test

Test the full system with a simple topic.

```bash
python research_orchestrator.py "Python programming"
```

**What happens:**

```
═══════════════════════════════════════════════════
Infinite Research Refinement System
with Parallel DuckDuckGo Search (1-10 queries)
Optimized for Weak Models: Last 2 refinements + KB/RAG
═══════════════════════════════════════════════════

Initializing research: Python programming...

╔═══ Input File Selection ═══╗

No files found in input directory
Place files in: C:\Users\rbgnr\git\InfiniteResearch\input

Options:
  0 - No input files (prompt only)
  ...

Select files (default: 0): 0  ← Just press Enter

Research ID: research-20250121-XXXXXX
Created research directory: ...

═══════════════════════════════════════════════════
Phase 1: Initial Research with Parallel Search
═══════════════════════════════════════════════════

[Agent analyzing topic...]
[Executing 5-7 parallel searches...]
[Synthesizing research document...]

✓ Saved refinement-0001.md
  Search terms used: python basics, ...

═══════════════════════════════════════════════════
Phase 2: Infinite Refinement Loop
═══════════════════════════════════════════════════

Press Ctrl+C to stop

Refinement 1 → 2
...
```

**Let it run for 2-3 refinements, then press Ctrl+C**

---

## Step 5: Check Output

```bash
# View generated files
ls generation/research-*/

# Expected:
refinement-0001.md
refinement-0002.md
refinement-0003.md
rag/vectors.db
kb/knowledge.db
memory/agent_memory.db
```

### View a refinement

```bash
cat generation/research-*/refinement-0001.md
```

**Should see:**
```markdown
<!-- RESEARCH_ID: research-20250121-XXXXXX -->
<!-- VERSION: 0001 -->
<!-- SEARCH_TERMS: python basics, python tutorial, ... -->
<!--
SOURCES:
  SOURCE: Python.org | https://python.org
  SOURCE: Real Python | https://realpython.com
  ...
-->

---

# Python Programming Research

[... research content ...]
```

**✓ Success indicators:**
- Metadata at top with research ID, version, search terms
- Sources listed
- Actual research content below

---

## Step 6: Test Input Files

### Create test input file

```bash
mkdir input
echo "Python is a high-level programming language." > input/notes.txt
```

### Run with input file

```bash
python research_orchestrator.py "Python programming"
```

**When prompted:**
```
Available files:
  2. notes.txt (50 B, TXT)

Select files: 2  ← Select the file
✓ Selected 1 file(s)
✓ Copied 1 input file(s) to session
```

**Check:** Refinement should reference your input file context.

---

## Troubleshooting

### Error: "Connection refused"

**Problem:** Can't connect to LMStudio

**Solution:**
1. Check LMStudio is running
2. Check server started (green indicator)
3. Verify port: `http://localhost:1234`
4. Test with curl:
   ```bash
   curl http://localhost:1234/v1/models
   ```

### Error: "Model not found"

**Problem:** Model name doesn't match

**Solution:**
1. Check exact model name in LMStudio
2. Update config.yaml
3. Model names are case-sensitive!

### Error: "Import error: ddgs"

**Problem:** duckduckgo-search not installed

**Solution:**
```bash
pip install duckduckgo-search
```

### Error: "No module named 'agno'"

**Problem:** Agno not installed

**Solution:**
```bash
pip install agno
```

### Search returns no results

**Problem:** DuckDuckGo might be rate-limiting

**Solution:**
1. Wait a minute
2. Reduce number of parallel searches
3. Increase timeout in config

### Refinements not improving

**Problem:** Weak model needs more iterations

**Solution:**
1. Let it run 10-15 iterations
2. Check search terms are evolving (view files)
3. Increase refinement_delay to give model more time

---

## Performance Testing

### Test with different numbers of parallel searches

Edit `agents/research_agent.py`:

```python
# Try different configurations:

# Minimal (fast, less comprehensive)
parallel_search = ParallelDuckDuckGoSearch(
    max_results_per_query=2
)

# Balanced (default)
parallel_search = ParallelDuckDuckGoSearch(
    max_results_per_query=5
)

# Comprehensive (slower, more thorough)
parallel_search = ParallelDuckDuckGoSearch(
    max_results_per_query=10
)
```

### Monitor performance

```bash
# Watch logs in real-time
tail -f research.log

# Check iteration time
# Should see logs like:
# [INFO] Refinement 2 complete. Waiting 10s...
```

---

## Validation Checklist

Run through this checklist to ensure everything works:

- [ ] `python test_setup.py` passes
- [ ] `python test_parallel_search.py` passes
- [ ] LMStudio server running
- [ ] `config.yaml` updated with model name
- [ ] LMStudio connection test works
- [ ] `python research_orchestrator.py "Test"` runs
- [ ] File selection prompt appears
- [ ] Initial research generates
- [ ] refinement-0001.md created
- [ ] Metadata includes sources
- [ ] Refinement loop starts
- [ ] refinement-0002.md created
- [ ] Ctrl+C stops gracefully
- [ ] Input files can be selected
- [ ] Input file content used in research

---

## Next Steps

Once all tests pass:

1. **Try a real research topic:**
   ```bash
   python research_orchestrator.py "Impact of AI on healthcare"
   ```

2. **Let it run longer** (10-20 iterations for weak models)

3. **Compare refinements:**
   ```bash
   diff generation/research-*/refinement-0001.md \
        generation/research-*/refinement-0010.md
   ```

4. **Check source evolution:**
   ```bash
   grep "SOURCES:" generation/research-*/refinement-*.md
   ```

5. **Analyze search term evolution:**
   ```bash
   grep "SEARCH_TERMS:" generation/research-*/refinement-*.md
   ```

---

## Success Criteria

System is working correctly if:

✓ Dependencies install without errors
✓ Parallel search returns structured results
✓ LMStudio connects and responds
✓ Initial research generates with sources
✓ Refinement loop improves content
✓ Search terms evolve each iteration
✓ Sources are tracked in metadata
✓ KB/RAG databases are created
✓ Ctrl+C stops gracefully
✓ Output files are properly formatted

---

**You're ready to do serious research!** 🚀
