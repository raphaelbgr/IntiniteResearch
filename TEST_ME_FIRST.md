# Test Me First - 5 Minute Quick Test

Follow these steps in order:

## 1. Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

Wait for installation to complete.

---

## 2. Test Setup (30 seconds)

```bash
python test_setup.py
```

**Expected:**
```
Testing imports...
✓ agno (installed)
✓ openai (x.x.x)
✓ duckduckgo-search (ddgs)
✓ pydantic (x.x.x)
...
✓ All tests passed! System is ready.
```

**If fails:** Check error messages and install missing packages.

---

## 3. Test Parallel Search (1 min)

**No LMStudio needed for this test!**

```bash
python test_parallel_search.py
```

**Expected:**
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

✓ All tests completed!
```

**This proves web search works!**

---

## 4. Configure LMStudio (2 min)

### A. Start LMStudio
1. Open LMStudio app
2. Load a model (e.g., `llama-3.1-8b-instruct`)
3. Click "Start Server" button
4. Note the model name

### B. Update Config

Edit `config.yaml`:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  model: "llama-3.1-8b-instruct"  # ← Change to YOUR model name
```

### C. Test Connection

```bash
python -c "from openai import OpenAI; client = OpenAI(base_url='http://localhost:1234/v1', api_key='lm-studio'); print('✓ Connected to LMStudio')"
```

**Expected:** `✓ Connected to LMStudio`

---

## 5. Quick Research Test (30 seconds)

```bash
python research_orchestrator.py "Python programming"
```

**What you'll see:**

```
═══ Input File Selection ═══
No files found in input directory

Select files (default: 0):
```

**Just press Enter** (0 for no input files)

**Then:**
```
Research ID: research-20250121-XXXXXX
Created research directory

Phase 1: Initial Research
Agent will use parallel DuckDuckGo search

[Agent thinking and searching...]
```

**Let it run for 1-2 refinements (2-3 minutes), then press Ctrl+C**

---

## 6. Check Results

```bash
# View generated files
ls generation/research-*/

# Expected:
refinement-0001.md
refinement-0002.md
refinement-0003.md
rag/
kb/
memory/
```

### View first refinement

```bash
cat generation/research-*/refinement-0001.md
```

**Should see:**
```markdown
<!-- RESEARCH_ID: research-... -->
<!-- VERSION: 0001 -->
<!-- SEARCH_TERMS: python basics, ... -->
<!--
SOURCES:
  SOURCE: Python.org | https://python.org
  SOURCE: Real Python | https://realpython.com
-->

---

# Python Programming Research
...
```

---

## ✓ Success!

If you see:
- ✓ Metadata at top of file
- ✓ Search terms listed
- ✓ Sources with URLs
- ✓ Actual research content

**Your system is working perfectly!**

---

## What If It Fails?

### "Connection refused to LMStudio"

**Check:**
```bash
curl http://localhost:1234/v1/models
```

Should return model list. If not:
- LMStudio not running
- Server not started in LMStudio
- Wrong port

### "Model not found"

**Check model name:**
1. Look at LMStudio's UI
2. See exact model name
3. Update config.yaml exactly

### "Search failed"

**Check internet:**
```bash
python test_parallel_search.py
```

If this works but orchestrator fails, it's an LMStudio issue.

### Agent produces gibberish

**Try:**
- Better model (13B instead of 7B)
- Lower temperature in config (0.5 instead of 0.7)
- Let it run more iterations (10+)

---

## Next: Real Research

Once quick test passes:

### 1. Add Input Files (Optional)

```bash
mkdir input
# Add your PDFs, notes, etc.
cp ~/Documents/research_paper.pdf input/
```

### 2. Run Real Research

```bash
python research_orchestrator.py "Your actual research topic"
```

### 3. Select Input Files

```
Select files: 1  ← Select all files
```

### 4. Let It Run

**For weak models (7B-13B):** Let it run 10-20 iterations
**For strong models (70B+):** 5-10 iterations enough

### 5. Monitor Progress

```bash
# Watch log file
tail -f research.log

# Check latest version
ls -lt generation/research-*/refinement-*.md | head -1
```

---

## Full Test Sequence

Run all tests in order:

```bash
# 1. Setup
python test_setup.py

# 2. Search tool
python test_parallel_search.py

# 3. Quick research
python research_orchestrator.py "Python programming"
# Press Enter for no input files
# Wait 2-3 minutes
# Press Ctrl+C

# 4. Check output
cat generation/research-*/refinement-0001.md

# 5. Success!
```

**Total time: ~5 minutes**

---

## Quick Reference

```bash
# Install
pip install -r requirements.txt

# Test setup
python test_setup.py

# Test search
python test_parallel_search.py

# Test full system
python research_orchestrator.py "Test topic"

# Check results
ls generation/
cat generation/research-*/refinement-*.md
```

---

**That's it! Start with `python test_setup.py` and work your way down.** 🚀
