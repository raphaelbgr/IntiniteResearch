# How To Test - Step by Step Tutorial

## Prerequisites

- Python 3.10+ installed
- Terminal/Command Prompt open
- Internet connection (for web searches)

## Step-by-Step Instructions

### Step 1: Install Dependencies

Open your terminal in the InfiniteResearch directory:

```bash
cd ~/git\InfiniteResearch
```

Install all required packages:

```bash
pip install -r requirements.txt
```

**What this installs:**
- `agno` - Agent framework
- `openai` - For LMStudio API
- `duckduckgo-search` - Web search
- `pydantic` - Data validation
- `rich` - Beautiful terminal output
- And more...

**Wait for it to complete** (may take 1-2 minutes)

---

### Step 2: Verify Installation

Run the setup test:

```bash
python test_setup.py
```

**You should see:**
```
╔════════════════════════════════════╗
║ Testing imports...                 ║
║ ✓ agno (installed)                ║
║ ✓ openai (1.x.x)                  ║
║ ✓ duckduckgo-search (ddgs)        ║
║ ✓ pydantic (2.x.x)                ║
║ ...                                ║
╚════════════════════════════════════╝

Test Summary
Dependencies         ✓ PASS
Project Imports      ✓ PASS
Configuration        ✓ PASS

✓ All tests passed! System is ready.
```

**If you see ✗ FAIL:**
- Read the error message
- Install missing package: `pip install <package-name>`
- Run test again

---

### Step 3: Test Parallel Search (No LMStudio Needed!)

This tests web search without requiring LMStudio:

```bash
python test_parallel_search.py
```

**You should see beautiful output:**
```
╔════════════════════════════════════╗
║ Test 1: Single Search Query       ║
╚════════════════════════════════════╝

Total queries: 1
Successful: 1
Total results: 3
Unique sources: 3

┌─ First source ─────────────────────┐
│ Title: Python Tutorial             │
│ URL: https://python.org/tutorial   │
│ Snippet: Python is a powerful...   │
└────────────────────────────────────┘

...

✓ All tests completed!
```

**This proves:**
- ✓ Internet connection works
- ✓ DuckDuckGo search works
- ✓ Parallel execution works
- ✓ Source tracking works

---

### Step 4: Setup LMStudio

#### A. Download and Install LMStudio
- Go to: https://lmstudio.ai
- Download for your OS
- Install and open

#### B. Download a Model

In LMStudio:
1. Click "Search" icon
2. Search for: `llama-3.1-8b-instruct`
3. Download the model (wait for download)
4. Click "Load" when ready

**Recommended models:**
- **7B**: Fast, good for testing
  - `llama-3.1-7b-instruct`
  - `mistral-7b-instruct`

- **13B**: Balanced
  - `llama-3.1-13b-instruct`

#### C. Start Server

1. Click the "Server" icon in LMStudio
2. Click "Start Server"
3. Should show: `Server running on http://localhost:1234`

#### D. Note Model Name

Look at the loaded model name in LMStudio (top bar).

Example: `llama-3.1-8b-instruct-q4` or just `llama-3.1-8b-instruct`

**Copy this exact name!**

---

### Step 5: Update Configuration

Edit `config.yaml` in a text editor:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  model: "llama-3.1-8b-instruct"  # ← Paste YOUR model name here
  temperature: 0.7
  max_tokens: 2048
```

**Save the file.**

---

### Step 6: Test LMStudio Connection

Quick test to verify LMStudio is working:

```bash
python -c "from openai import OpenAI; client = OpenAI(base_url='http://localhost:1234/v1', api_key='lm-studio'); response = client.chat.completions.create(model='llama-3.1-8b-instruct', messages=[{'role': 'user', 'content': 'Say hello in 5 words'}], max_tokens=20); print('✓ LMStudio works!'); print('Response:', response.choices[0].message.content)"
```

**Expected:**
```
✓ LMStudio works!
Response: Hello there, how are you?
```

**If it fails:**
- Check LMStudio server is running (green "Server Running")
- Check model name matches exactly
- Check port is 1234

---

### Step 7: Quick Research Test

Now test the full system with a simple topic:

```bash
python research_orchestrator.py "What is Python programming?"
```

**You'll see beautiful output:**

```
╔══════════════════════════════════════════════════╗
║ Infinite Research Refinement System              ║
║ Powered by Agno + LMStudio                       ║
║ Parallel DuckDuckGo Search (1-10 queries)        ║
║ Optimized for Weak Models                        ║
╚══════════════════════════════════════════════════╝

LLM Model:      llama-3.1-8b-instruct
Server:         http://localhost:1234/v1

─────────────────── Initialization ───────────────────

Topic: What is Python programming?

╔═══ Input File Selection ═══╗

No files found in input directory
Place files in: ~/git\InfiniteResearch\input

Options:
  0 - No input files (prompt only)

Select files (default: 0):
```

**Just press Enter** (select 0 for no files)

**Continue watching:**

```
✓ Research ID: research-20250121-XXXXXX

─────────────── Phase 1: Initial Research ───────────────

Agent will execute parallel DuckDuckGo searches

[Agent is thinking and searching the web...]

┌─────── Parallel Search Execution ──────┐
│ #  Query                  Status       │
├────────────────────────────────────────┤
│ 1  python basics          Searching... │
│ 2  python tutorial        Searching... │
│ 3  python applications    Searching... │
│ ...                                    │
└────────────────────────────────────────┘

╔═══════ Search Complete ════════╗
║ Queries Executed: 5             ║
║ Total Results: 25               ║
║ Unique Sources: 25              ║
╚═════════════════════════════════╝

✓ Initial research completed: refinement-0001.md
  Search terms: python basics, python tutorial, ...

┌────────── Sources Consulted (25 total) ──────────┐
│ #  Title                    URL                  │
├──────────────────────────────────────────────────┤
│ 1  Python.org               https://python.org   │
│ 2  Real Python              https://realpython..│
│ 3  Python Tutorial          https://docs.pytho..│
│ ...                                              │
└──────────────────────────────────────────────────┘

─────────────── Phase 2: Infinite Refinement ────────────

╔═══════════ Strategy ════════════╗
║ • Context: Last 2 refinements   ║
║ • Learning: Search terms evolve ║
║ • Stop: Press Ctrl+C            ║
╚═════════════════════════════════╝

Starting infinite refinement loop

────────── Refinement 1 → 2 ──────────

  Search Terms:     6 queries
  Gaps Identified:  2 areas
  Document Size:    2,547 characters

[Agent searching and refining...]

✓ Refinement 2 complete
  Waiting 10s before next iteration...
```

**Let it run for 2-3 refinements (3-5 minutes), then:**

**Press `Ctrl+C`** to stop

```
^C

Received interrupt signal...
Stopping refinement loop...

─────────────────── Cleanup ─────────────────────

✓ Vector store closed

╔═══════ ✓ Research Session Complete ════════╗
║ Research ID:      research-20250121-XXXXXX ║
║ Total Refinements: 3                       ║
║ Sources Consulted: 42                      ║
║ Output Directory:  generation/research-... ║
╚════════════════════════════════════════════╝
```

---

### Step 8: Check Your Results

```bash
# Navigate to output directory
cd generation

# List research sessions
ls

# You should see:
research-20250121-XXXXXX/

# Go into it
cd research-20250121-XXXXXX

# List files
ls

# You should see:
refinement-0001.md
refinement-0002.md
refinement-0003.md
rag/
kb/
memory/
input/  (if you used input files)
```

### View your research

```bash
# Windows
type refinement-0001.md

# Linux/Mac
cat refinement-0001.md
```

**You should see:**
```markdown
<!-- RESEARCH_ID: research-20250121-XXXXXX -->
<!-- VERSION: 0001 -->
<!-- SEARCH_TERMS: python basics, python tutorial, python features -->
<!--
SOURCES:
  SOURCE: Python.org Official | https://python.org
  SOURCE: Real Python Tutorials | https://realpython.com
  SOURCE: W3Schools Python | https://w3schools.com/python
  ...
-->

---

# Python Programming Research

## Introduction

Python is a high-level programming language...

[... rest of research ...]
```

---

## What To Look For (Success Indicators)

### ✓ Metadata Present
- Research ID at top
- Version number
- Search terms used
- Sources with URLs

### ✓ Content Quality
- Structured with headings
- Multiple sections
- Information from web searches
- Coherent and readable

### ✓ Source Tracking
- 10-30 sources listed
- Real URLs
- Titles match URLs

### ✓ Evolution
Compare refinement-0001.md vs refinement-0003.md:
- More detailed
- Better organized
- Additional information
- Improved clarity

---

## Common Issues & Solutions

### Issue: "Import error: agno"

**Solution:**
```bash
pip install agno
```

### Issue: "Connection refused"

**Solution:**
1. Check LMStudio is running
2. Click "Start Server" in LMStudio
3. Check green "Server Running" indicator

### Issue: "Model not found"

**Solution:**
1. Look at model name in LMStudio (exact name!)
2. Update `config.yaml` with exact name
3. Case-sensitive!

### Issue: Search returns nothing

**Solution:**
1. Check internet connection
2. Try: `python test_parallel_search.py`
3. If that works, issue is with LMStudio

### Issue: Slow performance

**Solution:**
1. Use smaller model (7B instead of 13B)
2. Reduce `max_tokens` in config to 1024
3. Increase `refinement_delay` to 20 seconds

### Issue: Poor quality output

**Solution:**
1. Use better model (13B instead of 7B)
2. Let it run more iterations (10-20)
3. Provide input files with context

---

## Testing With Input Files

### Create test input

```bash
# Create input folder
mkdir input

# Add a test file
echo "Python is known for readability and simplicity." > input/notes.txt

# Or copy existing files
cp ~/Documents/python_notes.pdf input/
```

### Run research

```bash
python research_orchestrator.py "Python programming"
```

### Select files

```
╔═══ Input File Selection ═══╗

Available Input Files:

ID  Filename      Size    Type
──  ────────────  ──────  ────
2   notes.txt     50 B    TXT

Select files: 2  ← Type 2 and press Enter

✓ Selected 1 file(s):
  • notes.txt
```

**The file content will be included in all iterations!**

---

## Advanced: Monitor in Real-Time

### Terminal 1: Run Research
```bash
python research_orchestrator.py "Your topic"
```

### Terminal 2: Watch Files Being Created
```bash
# Windows PowerShell
Get-ChildItem generation\research-*\refinement-*.md | Sort-Object LastWriteTime

# Linux/Mac
watch -n 2 'ls -lt generation/research-*/refinement-*.md'
```

### Terminal 3: Watch Logs
```bash
tail -f research.log
```

**You'll see research happening in real-time!**

---

## Quickest Test (TL;DR)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test imports
python test_setup.py

# 3. Test search
python test_parallel_search.py

# 4. Start LMStudio with a model + server

# 5. Update config.yaml with model name

# 6. Run research
python research_orchestrator.py "Test topic"
# Press Enter at file selection
# Wait 3-5 minutes
# Press Ctrl+C

# 7. Check output
cat generation/research-*/refinement-0001.md

# ✓ Done!
```

---

## What You Should See (Beautiful CLI Output)

The system now has **gorgeous terminal output** with:

- 🎨 **Colorful banners** for each phase
- 📊 **Tables** showing sources and search results
- 📈 **Progress indicators** for long operations
- ✨ **Status panels** with borders
- 🎯 **Clear section headers** with rules
- ✓ **Success/error indicators** with symbols
- 📋 **Structured data display** in tables

**Example screenshots** (in your terminal):

```
╔══════════════════════════════════════════════════╗
║ Infinite Research Refinement System              ║
║ Powered by Agno + LMStudio                       ║
╚══════════════════════════════════════════════════╝

────────────────── Refinement 2 → 3 ──────────────────

  Search Terms:     7 queries
  Gaps Identified:  3 areas
  Document Size:    3,421 characters

┌──────── Sources Consulted (42 total) ────────────┐
│ #  Title                           URL           │
├───────────────────────────────────────────────────┤
│ 1  Python.org                      https://...   │
│ 2  Real Python                     https://...   │
│ 3  W3Schools Python                https://...   │
└───────────────────────────────────────────────────┘
```

**It's beautiful!** 🎨

---

## Next Steps After Testing

Once everything works:

1. **Try real research topics**
2. **Add your own input files**
3. **Let it run for 10-20 iterations**
4. **Compare early vs late refinements**
5. **Analyze search term evolution**

---

## Getting Help

If stuck:
1. Check error messages carefully
2. Read `TESTING.md` for detailed troubleshooting
3. Check `README.md` for full documentation
4. Verify LMStudio is running with: `curl http://localhost:1234/v1/models`

---

**Start with `python test_setup.py` and follow the steps!** 🚀
