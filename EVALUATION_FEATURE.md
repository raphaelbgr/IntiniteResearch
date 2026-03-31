# Evaluation Feature - Self-Assessment Loop

## Overview

The system now includes a **special evaluation loop** that compares research progress against your objectives and generates progress reports.

## How It Works

```
Normal Refinement Loop:
  Iteration 1 → refinement-0002.md
  Iteration 2 → refinement-0003.md
  ...
  Iteration 10 → refinement-0011.md
      ↓
  ┌──────────────────────────────────────────┐
  │  SPECIAL EVALUATION LOOP (every 10)      │
  │  ────────────────────────────────────    │
  │  1. Load latest refinement               │
  │  2. Load original prompt                 │
  │  3. Load input files                     │
  │  4. AI compares and evaluates:           │
  │     - Objective alignment (1-10)         │
  │     - Completeness (1-10)                │
  │     - Gaps identified                    │
  │     - Strengths noted                    │
  │     - Recommendations                    │
  │     - Progress percentage                │
  │  5. Save to /report/report-0001.md       │
  └──────────────────────────────────────────┘
      ↓
  Continue refinement:
  Iteration 11 → refinement-0012.md
  ...
  Iteration 20 → refinement-0021.md
      ↓
  EVALUATION LOOP again → /report/report-0002.md
      ↓
  Continue infinitely...
```

## Key Innovation: Delayed Input Files

### Strategy for Weak Models

**The Flaw You Identified:**
Adding input files immediately → AI tries to match them from iteration 1 → May just copy/paraphrase instead of learning.

**The Solution:**
```
Iterations 1-10:
  • AI learns on its own from web searches
  • Builds foundational understanding
  • No input file influence
  • Pure discovery

Iteration 10:
  • Input files UNLOCKED 🔓
  • Special evaluation compares research vs input
  • AI sees how close it got

Iterations 11+:
  • AI now has input files as context
  • Can integrate user's domain knowledge
  • Refined with both learned + provided knowledge
```

**Why this is brilliant:**
✓ AI develops own understanding first
✓ Avoids just copying input files
✓ Evaluation shows how well AI learned independently
✓ Then combines AI research + user knowledge
✓ Best of both worlds!

## Output Structure

```
generation/research-XXXXX/
  ├── refinement-0001.md    # Pure AI research
  ├── refinement-0002.md
  ├── ...
  ├── refinement-0010.md    # Before input unlock
  ├── refinement-0011.md    # After input unlock (includes user files)
  ├── ...
  ├── refinement-0020.md
  │
  └── report/               # NEW: Evaluation reports
      ├── report-0001.md    # After iteration 10
      ├── report-0002.md    # After iteration 20
      ├── report-0003.md    # After iteration 30
      └── ...
```

## Report Format

```markdown
<!-- REPORT_NUMBER: 0001 -->
<!-- EVALUATED_VERSION: 0010 -->
<!-- TIMESTAMP: 2025-01-21T14:30:22 -->

---

# Research Progress Evaluation - Report #1

## Evaluation of: Quantum Computing Research
**Refinement Version:** 0010
**Iterations Completed:** 10

---

## 1. Objective Alignment: 8/10

The research addresses the original topic well, covering fundamentals,
algorithms, hardware, and applications. However, missing some advanced
topics from user's reference materials.

## 2. Completeness: 7/10

Covers main areas but lacks depth in:
- Quantum error correction details
- Industry-specific applications
- Recent 2025 breakthroughs

## 3. Alignment with Reference Materials: 6/10

The research independently discovered 60% of what's in the user's PDF.
Missing key sections on:
- NISQ-era algorithms
- Fault-tolerant quantum computing

## 4. Research Gaps

- Missing detailed case studies from industry
- Quantum supremacy discussion too brief
- No coverage of quantum cryptography
- Limited discussion of challenges

## 5. Strengths

- Excellent foundational coverage
- Clear, well-structured document
- Good source diversity (30+ sources)
- Recent information from 2025

## 6. Recommendations

- Add case studies from IBM, Google Quantum teams
- Expand error correction section with technical details
- Include quantum cryptography discussion
- Add more depth to hardware implementation

## 7. Overall Progress: 65%

The research is 65% complete toward fully addressing the objective.
Strong foundation established. Next iterations should focus on depth
and integration with user's reference materials.

---

**Next Steps:**
✓ Input files now unlocked - AI will integrate user knowledge
✓ Focus on identified gaps
✓ Add recommended case studies
✓ Deepen technical sections
```

## Configuration

### config.yaml

```yaml
research:
  # Input file delay (default: 10)
  input_delay: 10
  # 0 = include immediately
  # 10 = include after 10 iterations
  # -1 = never include

  # Evaluation settings (default: enabled, every 10)
  enable_evaluation: true
  evaluation_frequency: 10
```

### Command-Line Override

```cmd
# Default: Input after 10, evaluate every 10
python research_orchestrator.py "Topic"

# Custom: Input after 5, evaluate every 5
python research_orchestrator.py "Topic" --input-delay 5 --eval-freq 5

# No evaluation
python research_orchestrator.py "Topic" --no-eval

# Input immediately
python research_orchestrator.py "Topic" --input-delay 0

# Evaluate more frequently
python research_orchestrator.py "Topic" --eval-freq 3
```

## Example Timeline

### With Defaults (input-delay=10, eval-freq=10)

```
Iteration 1-9:
  • Pure AI research from web
  • Learning independently
  • No input file influence

Iteration 10:
  ┌─ EVALUATION #1 ──────────────────────┐
  │ Compare refinement-0010.md with:     │
  │ • Original prompt                    │
  │ • Input files                        │
  │ Generate: report-0001.md             │
  │ Result: "60% complete, gaps X,Y,Z"   │
  └──────────────────────────────────────┘
  🔓 INPUT FILES UNLOCKED

Iteration 11-19:
  • AI now has input files
  • Integrates user knowledge
  • Fills identified gaps

Iteration 20:
  ┌─ EVALUATION #2 ──────────────────────┐
  │ Compare refinement-0020.md with:     │
  │ • Original prompt                    │
  │ • Input files                        │
  │ Generate: report-0002.md             │
  │ Result: "85% complete, minor gaps"   │
  └──────────────────────────────────────┘

Iteration 21-29:
  • Continued refinement

Iteration 30:
  ┌─ EVALUATION #3 ──────────────────────┐
  │ Generate: report-0003.md             │
  │ Result: "95% complete, excellent!"   │
  └──────────────────────────────────────┘

... continues infinitely
```

## Beautiful CLI Output

When evaluation runs:

```
════════════════════════════════════════════════
 Iteration 10: EVALUATION CHECKPOINT
════════════════════════════════════════════════

🔓 UNLOCKING INPUT FILES (after 10 iterations)

──────────────── Evaluation Loop ────────────────

Evaluating refinement 0010
Evaluation iteration: 1

[AI analyzing research vs objectives...]

┌───────── Evaluation Complete ─────────┐
│ Objective Alignment:    8/10          │
│ Completeness:           7/10          │
│ Overall Progress:       65%           │
│ Gaps Identified:        4             │
└───────────────────────────────────────┘

✓ Evaluation report saved: report-0001.md

══════════════════════════════════════════════════

Continuing refinement with input files included...
```

## Use Cases

### 1. Research Quality Control

**Problem:** How good is my research?

**Solution:** Check evaluation reports
```cmd
cd generation\research-XXXXX\report
type report-0001.md
```

See objective scores, gaps, progress percentage.

### 2. Guided Improvement

**Problem:** What should AI focus on?

**Solution:** Evaluation identifies gaps automatically
- AI reads gaps from report
- Next iterations target those gaps
- Self-correcting research

### 3. Convergence Tracking

**Problem:** When to stop?

**Solution:** Monitor progress in reports
```
Report #1 (iteration 10):  65% complete
Report #2 (iteration 20):  85% complete
Report #3 (iteration 30):  95% complete
```

When progress plateaus → stop refining.

### 4. Input File Effectiveness

**Problem:** Are my input files helping?

**Solution:** Compare pre/post input unlock
```
Before unlock (report-0001.md): 60% alignment
After unlock (report-0002.md):  85% alignment

→ Input files added 25% value!
```

## Configuration Examples

### Quick Feedback (Every 5 Iterations)

```cmd
python research_orchestrator.py "Topic" --eval-freq 5
```

**Use when:**
- Testing the system
- Quick research
- Need frequent checkpoints

### Long-term Research (Every 20 Iterations)

```yaml
# config.yaml
research:
  evaluation_frequency: 20
```

**Use when:**
- Deep research topics
- Letting it run overnight
- Less frequent interruptions

### No Input Files (Pure AI)

```cmd
python research_orchestrator.py "Topic" --input-delay -1
```

**Use when:**
- No reference materials available
- Want pure AI-generated research
- Testing AI capabilities

### Immediate Input Integration

```cmd
python research_orchestrator.py "Topic" --input-delay 0
```

**Use when:**
- Input files are critical
- Want maximum alignment from start
- Specific requirements in files

## Benefits

### For Weak Models

✓ **Learn First, Compare Later**
- AI builds understanding before seeing answers
- Avoids dependency on input files
- Better independent reasoning

✓ **Guided Improvement**
- Evaluation identifies weak areas
- Focuses future iterations
- Efficient use of limited model capacity

✓ **Progress Tracking**
- Know when research is "good enough"
- See improvement over time
- Data-driven stopping point

### For Strong Models

✓ **Quality Assurance**
- Automated quality checks
- Objective scoring
- Systematic gap analysis

✓ **Alignment Verification**
- Ensures research stays on topic
- Catches drift early
- Corrects course automatically

## Advanced Usage

### Custom Evaluation Frequency Per Phase

```cmd
# Phase 1: Frequent evaluation (learning phase)
python research_orchestrator.py "Topic" --eval-freq 5

# After 20 iterations, stop and restart with:
# Phase 2: Less frequent (refinement phase)
python research_orchestrator.py "Same Topic" --eval-freq 20
```

### Evaluation-Only Mode (Future Feature)

```python
# Could add:
python research_orchestrator.py "Topic" --eval-only --version 25
# Runs evaluation on existing refinement without continuing
```

## File Organization

```
generation/research-XXXXX/
  ├── input/                # User files copied here
  │   └── notes.txt
  │
  ├── refinement-0001.md   # Iterations 1-10: No input context
  ├── ...
  ├── refinement-0010.md
  │
  ├── refinement-0011.md   # Iterations 11+: With input context
  ├── ...
  ├── refinement-0030.md
  │
  ├── report/              # Evaluation reports
  │   ├── report-0001.md   # After iteration 10
  │   ├── report-0002.md   # After iteration 20
  │   └── report-0003.md   # After iteration 30
  │
  ├── rag/vectors.db
  └── kb/knowledge.db
```

## Summary

**New Features:**
1. ✅ Delayed input files (default: after 10 iterations)
2. ✅ Evaluation loop (default: every 10 iterations)
3. ✅ Progress reports in /report folder
4. ✅ CLI parameters for customization
5. ✅ Beautiful CLI output for evaluations

**Benefits:**
- Weak models learn independently first
- Self-assessment and course correction
- Track progress toward objectives
- Automated quality control
- Flexible, configurable

**Usage:**
```cmd
# Default (recommended)
python research_orchestrator.py "Your topic"

# Custom settings
python research_orchestrator.py "Topic" --input-delay 5 --eval-freq 5

# Disable evaluation
python research_orchestrator.py "Topic" --no-eval
```

---

**This makes the system self-aware and self-improving!** 🧠✨
