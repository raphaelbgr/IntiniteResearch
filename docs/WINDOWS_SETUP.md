# Windows Setup Guide

## Quick Install (Easiest)

### Option 1: Run Install Script

Double-click `install.bat` or run:

```cmd
install.bat
```

This will:
1. Install all dependencies
2. Test the installation
3. Test parallel search
4. Show next steps

**That's it!** Skip to Step 3 below.

---

### Option 2: Manual Install

If you prefer manual installation:

#### Step 1: Install Dependencies

```cmd
python -m pip install -r requirements.txt
```

**Note:** Use `python -m pip` instead of just `pip` on Windows.

#### Step 2: Verify Installation

```cmd
python test_setup.py
```

Should show:
```
✓ agno (installed)
✓ openai
✓ All tests passed!
```

#### Step 3: Test Search Tool

```cmd
python test_parallel_search.py
```

Should show search results with beautiful tables.

---

## Step 3: Setup LMStudio

### Download LMStudio

1. Go to: https://lmstudio.ai
2. Download Windows version
3. Install it
4. Open LMStudio

### Download a Model

In LMStudio:
1. Click "🔍 Search" icon
2. Search: `llama-3.1-8b-instruct`
3. Click "Download"
4. Wait for download (1-4 GB)

**Recommended models:**
- **llama-3.1-8b-instruct** (fast, good quality)
- **mistral-7b-instruct** (very fast)
- **llama-3.1-13b-instruct** (slower, better quality)

### Load Model

1. Click on the downloaded model
2. Click "Load Model"
3. Wait for it to load (green checkmark)

### Start Server

1. Click "↔️ Server" icon (left sidebar)
2. Click "Start Server" button
3. Should show: `Server running on http://localhost:1234`
4. Keep LMStudio running!

### Note Model Name

Look at the top of LMStudio - it shows the loaded model name.

**Copy this exact name!**

Example: `llama-3.1-8b-instruct` or `llama-3.1-8b-instruct-q4_k_m`

---

## Step 4: Configure

### Edit config.yaml

Right-click `config.yaml` → Open with Notepad

Change these lines:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  model: "llama-3.1-8b-instruct"  # ← Paste YOUR model name here
  temperature: 0.7
  max_tokens: 2048
```

**Save the file.**

---

## Step 5: Test LMStudio Connection

```cmd
python -c "from openai import OpenAI; client = OpenAI(base_url='http://localhost:1234/v1', api_key='lm-studio'); response = client.chat.completions.create(model='llama-3.1-8b-instruct', messages=[{'role': 'user', 'content': 'Say hello'}], max_tokens=20); print('Success! LMStudio connected'); print(response.choices[0].message.content)"
```

**Should print:**
```
Success! LMStudio connected
Hello! How can I help you?
```

**If it fails:**
- Check LMStudio is running
- Check server started (green indicator)
- Check model name in config.yaml matches exactly

---

## Step 6: Run Your First Research

```cmd
python research_orchestrator.py "What is Python programming?"
```

**What you'll see:**

```
╔══════════════════════════════════════════════════╗
║ Infinite Research Refinement System              ║
║ Powered by Agno + LMStudio                       ║
║ Parallel DuckDuckGo Search (1-10 queries)        ║
║ Optimized for Weak Models                        ║
╚══════════════════════════════════════════════════╝

LLM Model:      llama-3.1-8b-instruct
Server:         http://localhost:1234/v1

────────────────── Initialization ────────────────────

Topic: What is Python programming?

╔═══ Input File Selection ═══╗

No files found in input directory

Select files (default: 0):
```

**Press Enter** (0 = no input files for testing)

**Watch it work!**

```
✓ Research ID: research-20250121-XXXXXX

────────────── Phase 1: Initial Research ──────────────

Agent will execute parallel DuckDuckGo searches

[Agent working with beautiful progress indicators...]

╔═══════ Search Complete ════════╗
║ Queries Executed: 6             ║
║ Total Results: 30               ║
║ Unique Sources: 30              ║
╚═════════════════════════════════╝

✓ Initial research completed: refinement-0001.md

┌──── Sources Consulted (30 total) ────┐
│ 1  Python.org  https://python.org    │
│ 2  Real Python https://realpython.com│
│ ...                                  │
└──────────────────────────────────────┘
```

**Let it run for 2-3 refinements (5-10 minutes), then:**

**Press `Ctrl+C`** to stop.

```
^C

Stopping refinement loop...

────────────────── Cleanup ──────────────────

✓ Vector store closed

╔═══════ ✓ Research Session Complete ════════╗
║ Research ID:       research-20250121-XXXXXX ║
║ Total Refinements: 3                        ║
║ Sources Consulted: 45                       ║
║ Output Directory:  generation\research-...  ║
╚═════════════════════════════════════════════╝
```

---

## Step 7: Check Results

```cmd
cd generation
dir

REM You should see: research-20250121-XXXXXX\

cd research-20250121-XXXXXX
dir

REM You should see:
REM refinement-0001.md
REM refinement-0002.md
REM refinement-0003.md
REM rag\
REM kb\
REM memory\
```

### View your research

```cmd
type refinement-0001.md
```

**Should show:**
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

[... your research content ...]
```

---

## Troubleshooting

### "python is not recognized"

**Install Python:**
1. Go to: https://www.python.org/downloads/
2. Download Python 3.10 or higher
3. **Important:** Check "Add Python to PATH" during installation
4. Restart terminal

### "ModuleNotFoundError: No module named 'agno'"

**Run:**
```cmd
python -m pip install -r requirements.txt
```

### "Connection refused to localhost:1234"

**Check LMStudio:**
1. LMStudio is open
2. Model is loaded (green checkmark)
3. Server is started (green "Server Running")
4. Port shows 1234

### "Model 'xyz' not found"

**Fix model name:**
1. Look at LMStudio's top bar
2. Copy exact model name
3. Update `config.yaml` with exact name (case-sensitive!)

---

## Quick Command Reference

```cmd
REM Install dependencies
python -m pip install -r requirements.txt

REM Test setup
python test_setup.py

REM Test search
python test_parallel_search.py

REM Run research
python research_orchestrator.py "Your topic"

REM View results
cd generation
dir
type research-*\refinement-0001.md
```

---

## Pro Tips for Windows

### Create a Virtual Environment (Recommended)

```cmd
REM Create virtual environment
python -m venv venv

REM Activate it
venv\Scripts\activate

REM Now install
python -m pip install -r requirements.txt

REM When done, deactivate:
deactivate
```

### Add Python to PATH (Permanent Fix)

1. Search Windows for "Environment Variables"
2. Click "Environment Variables" button
3. Under "User variables", find "Path"
4. Click "Edit"
5. Click "New"
6. Add: `C:\Users\rbgnr\AppData\Local\Programs\Python\Python3XX\Scripts`
7. OK, OK, OK
8. **Restart terminal**
9. Now `pip` will work directly!

---

## What to Expect (Timeline)

### Installation: 2-3 minutes
```
python -m pip install -r requirements.txt
[Installing packages...]
```

### LMStudio Setup: 5-10 minutes
- Download app: 2 min
- Download model: 3-5 min
- Load and start: 1 min

### First Test Run: 5-10 minutes
- Initial research: 2-3 min
- 2-3 refinements: 3-7 min

**Total: ~20 minutes to fully test the system**

---

## Start Here

```cmd
REM 1. Install (use python -m pip on Windows)
python -m pip install -r requirements.txt

REM 2. Test
python test_setup.py

REM 3. Continue with HOW_TO_TEST.md
```

**Good luck!** 🚀

---

## Need Help?

- **Setup issues:** Read `HOW_TO_TEST.md`
- **LMStudio help:** Check LMStudio docs at https://lmstudio.ai/docs
- **Python help:** Ensure Python 3.10+ is installed

**Remember:** Always use `python -m pip` instead of `pip` on Windows if pip isn't in PATH.
