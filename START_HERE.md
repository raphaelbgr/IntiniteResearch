# START HERE - Windows Quick Start

## You're on Windows - Use These Commands

### ⚡ Quick Install (One Command)

```cmd
install.bat
```

**OR** manually:

```cmd
python -m pip install -r requirements.txt
```

**Note:** Use `python -m pip` (not just `pip`) on Windows.

---

## Complete Test Sequence

Run these commands one by one:

### 1. Install
```cmd
python -m pip install -r requirements.txt
```
⏱️ Takes 2-3 minutes

### 2. Test Setup
```cmd
python test_setup.py
```
✓ Should show: "All tests passed!"

### 3. Test Search (no LMStudio needed)
```cmd
python test_parallel_search.py
```
✓ Should show search results in beautiful tables

### 4. Setup LMStudio
- Download from https://lmstudio.ai
- Install and open
- Download a model (e.g., llama-3.1-8b-instruct)
- Load the model
- Start server (should show port 1234)

### 5. Configure
Open `config.yaml` in Notepad and change:
```yaml
model: "llama-3.1-8b-instruct"  # Your model name
```

### 6. Run Research
```cmd
python research_orchestrator.py "Test topic"
```
Press Enter when asked for input files

Let it run 2-3 minutes, then **Ctrl+C** to stop

### 7. Check Results
```cmd
cd generation
dir
type research-*\refinement-0001.md
```

---

## That's It!

**Start with:**
```cmd
python -m pip install -r requirements.txt
```

**Then follow the steps above.** 🚀

**For detailed guide:** Read `WINDOWS_SETUP.md`
