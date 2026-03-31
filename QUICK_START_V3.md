# Quick Start - Version 3.0 with Evaluation

## Installation Complete ✅

You've already installed dependencies. Now test the new evaluation feature!

## New Feature: Self-Assessment Loop

### Default Behavior

```cmd
python research_orchestrator.py "Quantum computing"
```

**What happens:**

```
Iterations 1-10:
  • AI researches independently (no input files yet)
  • Learns from web searches
  • Builds own understanding

Iteration 10:
  ┌─ EVALUATION #1 ──────────────────────┐
  │ Compare research vs your objective    │
  │ Scores: Alignment 8/10, Complete 7/10 │
  │ Progress: 65%                         │
  │ Save: report/report-0001.md           │
  └───────────────────────────────────────┘
  🔓 INPUT FILES UNLOCKED

Iterations 11-20:
  • AI now has your input files
  • Integrates your knowledge
  • Fills gaps from evaluation

Iteration 20:
  ┌─ EVALUATION #2 ──────────────────────┐
  │ Progress: 85% (improved!)             │
  │ Save: report/report-0002.md           │
  └───────────────────────────────────────┘

... continues infinitely
```

## Command-Line Options

### Basic Usage

```cmd
# Default: input after 10, evaluate every 10
python research_orchestrator.py "Your topic"
```

### Custom Input Delay

```cmd
# Add input files after 5 iterations
python research_orchestrator.py "Topic" --input-delay 5

# Include input files immediately
python research_orchestrator.py "Topic" --input-delay 0

# Never include input files
python research_orchestrator.py "Topic" --input-delay -1
```

### Custom Evaluation Frequency

```cmd
# Evaluate every 5 iterations
python research_orchestrator.py "Topic" --eval-freq 5

# Evaluate every 20 iterations
python research_orchestrator.py "Topic" --eval-freq 20
```

### Disable Evaluation

```cmd
# No evaluation reports
python research_orchestrator.py "Topic" --no-eval
```

### Combined

```cmd
# Custom: input after 5, evaluate every 5
python research_orchestrator.py "AI ethics" --input-delay 5 --eval-freq 5
```

## Testing It

### 1. Quick Test (No Input Files)

```cmd
python research_orchestrator.py "Python programming" --input-delay 0 --eval-freq 3
```

**This will:**
- Skip input delay (you have no files yet)
- Evaluate every 3 iterations (faster for testing)
- Let you see evaluation reports quickly!

**Let it run 6-9 iterations (2 or 3 evaluations), then Ctrl+C**

### 2. Check Evaluation Reports

```cmd
cd generation\research-*\report
dir

# Should see:
report-0001.md  (after iteration 3)
report-0002.md  (after iteration 6)
report-0003.md  (after iteration 9)

type report-0001.md
```

**You'll see:**
```markdown
# Research Progress Evaluation - Report #1

## 1. Objective Alignment: 7/10
Research addresses the topic but needs more depth...

## 2. Completeness: 6/10
Main areas covered, but missing...

## 4. Research Gaps
- Missing concrete examples
- Need more technical details
- ...

## 7. Overall Progress: 60%
```

### 3. With Input Files

Create a test input file:

```cmd
mkdir input
echo "Python is used for web development, data science, and automation." > input\notes.txt
```

Run research:

```cmd
python research_orchestrator.py "Python programming" --input-delay 3 --eval-freq 3
```

**Watch for:**
```
Iteration 3:
════════════════════════════════════
 EVALUATION CHECKPOINT
════════════════════════════════════

🔓 UNLOCKING INPUT FILES (after 3 iterations)

──────── Evaluation Loop ────────

Evaluating how well AI learned vs your input...

✓ Evaluation report saved: report-0001.md
```

**Check the report** - it will compare AI's independent research against your input file!

## Output Structure

```
generation/research-XXXXX/
  ├── input/
  │   └── notes.txt         # Your files
  │
  ├── refinement-0001.md   # Pure AI (no input)
  ├── refinement-0002.md
  ├── refinement-0003.md   # Still no input
  ├── refinement-0004.md   # NOW has input (after delay)
  ├── ...
  │
  ├── report/              # NEW!
  │   ├── report-0001.md   # Evaluation after iteration 3
  │   ├── report-0002.md   # After iteration 6
  │   └── ...
  │
  ├── rag/
  └── kb/
```

## What To Look For

### In Refinement Files

**Before input unlock:**
```markdown
<!-- VERSION: 0003 -->
<!-- SEARCH_TERMS: python basics, python tutorial -->

# Python Programming

[AI's own research from web...]
```

**After input unlock:**
```markdown
<!-- VERSION: 0004 -->
<!-- SEARCH_TERMS: python web development, python data science -->

# Python Programming

[Now incorporates concepts from your input file...]
```

### In Evaluation Reports

```markdown
## 1. Objective Alignment: 8/10
## 2. Completeness: 7/10
## 3. Alignment with Reference Materials: 6/10
## 4. Research Gaps
- Gap 1
- Gap 2
## 7. Overall Progress: 65%
```

**Use this to:**
- Know when research is "good enough"
- Track improvement iteration-to-iteration
- See if input files are helping

## Configuration

Edit `config.yaml`:

```yaml
research:
  input_delay: 10          # Default: after 10 iterations
  enable_evaluation: true  # Default: enabled
  evaluation_frequency: 10 # Default: every 10 iterations
```

**Or use CLI args to override!**

## Benefits

✓ **Self-Assessment** - AI evaluates its own progress
✓ **Delayed Input** - AI learns independently first
✓ **Progress Tracking** - Know completion percentage
✓ **Gap Detection** - Automatic weak area identification
✓ **Flexible** - Configure via config or CLI args

## Try It Now!

```cmd
# Quick test (3-iteration cycles)
python research_orchestrator.py "Test topic" --eval-freq 3 --input-delay 3

# Let it run to 9-12 iterations
# Check: generation\research-*\report\report-*.md
```

---

**This makes your research system self-aware!** 🧠✨
