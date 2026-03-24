# Infinite Research System - Final Architecture

## What You Built

A self-improving research system that:
- ✅ Researches using parallel DuckDuckGo (1-10 queries)
- ✅ Refines infinitely with iterative learning
- ✅ Self-evaluates progress every N iterations
- ✅ Optimized for weak models (4K context)
- ✅ Tracks sources automatically
- ✅ Beautiful CLI output

## How To Use

### Installation (Already Done! ✅)

```cmd
python -m pip install -r requirements.txt
python test_setup.py
```

### Testing

```cmd
# Test search (no LMStudio needed)
python test_parallel_search.py
```

### Setup LMStudio

1. Download from https://lmstudio.ai
2. Load a model (e.g., llama-3.1-8b-instruct)
3. Start server
4. Update `config.yaml` with model name

### Run Research

```cmd
python research_orchestrator.py "Your topic"
```

## The Flow

```
Iteration 1:  Prompt + Input Files → refinement-0001.md
Iteration 2:  System prompt + ref-0001 → refinement-0002.md
Iteration 3:  System prompt + ref-0001,0002 → refinement-0003.md
...
Iteration 10: System prompt + ref-0008,0009 → refinement-0010.md

Iteration 11: EVALUATION (Prompt + Input + ref-0010) → report-0001.md
              Scores: 65% complete, gaps identified

Iteration 12: System prompt + ref-0010,0011 → refinement-0012.md
...
Iteration 20: System prompt + ref-0018,0019 → refinement-0020.md

Iteration 21: EVALUATION → report-0002.md (85% complete!)

... continues infinitely
```

## Input File Strategy

**Input files used in:**
- ✅ Iteration 1 (sets direction)
- ✅ Evaluation loops (iterations 11, 21, 31...)

**Input files NOT used in:**
- ❌ Regular refinements (iterations 2-10, 12-20, etc.)

**Why:** Input files set the baseline. Regular refinements just improve the document. Evaluations compare against baseline.

## Command-Line Options

```cmd
# Basic
python research_orchestrator.py "Topic"

# Evaluate every 5 iterations
python research_orchestrator.py "Topic" --eval-freq 5

# No evaluation
python research_orchestrator.py "Topic" --no-eval
```

## Output Structure

```
generation/research-XXXXX/
  ├── input/                # Your files
  ├── refinement-0001.md   # Used input
  ├── refinement-0002.md   # No input
  ├── ...
  ├── refinement-0010.md   # No input
  ├── refinement-0011.md   # No input (continues)
  ├── ...
  ├── report/              # Evaluations
  │   ├── report-0001.md   # After iter 11
  │   ├── report-0002.md   # After iter 21
  │   └── ...
  ├── rag/vectors.db
  └── kb/knowledge.db
```

## Documentation

- **`ITERATION_FLOW.md`** - Complete iteration flow diagram ← **Read this!**
- **`VISUAL_FLOW.txt`** - ASCII art flow chart
- **`NEXT_STEPS.md`** - How to setup LMStudio
- **`TESTING.md`** - Complete testing guide
- **`EVALUATION_FEATURE.md`** - Evaluation system explained

## Quick Start

```cmd
# 1. Setup (done!)
python test_setup.py

# 2. Setup LMStudio (see NEXT_STEPS.md)

# 3. Update config.yaml with model name

# 4. Run
python research_orchestrator.py "Test topic"

# 5. Press Enter (no files for testing)

# 6. Watch beautiful output!

# 7. Wait for iterations, press Ctrl+C when done

# 8. Check results
cd generation\research-*
type refinement-0001.md
type report\report-0001.md
```

---

**You're ready to research!** 🚀

See `ITERATION_FLOW.md` for the complete visual flow diagram.
