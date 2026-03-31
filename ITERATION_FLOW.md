# Iteration Flow - How It Actually Works

## The Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 1: Initial Research                                   │
├─────────────────────────────────────────────────────────────────┤
│ Input:                                                           │
│   • User's original prompt                                      │
│   • ALL input files from /input folder                          │
│                                                                  │
│ AI Process:                                                      │
│   • Analyzes objective + input context                          │
│   • Executes parallel web searches                              │
│   • Synthesizes research                                        │
│                                                                  │
│ Output:                                                          │
│   → refinement-0001.md                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 2: First Refinement                                   │
├─────────────────────────────────────────────────────────────────┤
│ Input:                                                           │
│   • System prompt: "Keep refining, search for more depth..."   │
│   • refinement-0001.md ONLY                                     │
│   • (NO input files)                                            │
│                                                                  │
│ AI Process:                                                      │
│   • Reviews refinement-0001.md                                  │
│   • Searches for improvements                                   │
│   • Adds depth and detail                                       │
│                                                                  │
│ Output:                                                          │
│   → refinement-0002.md                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 3: Second Refinement                                  │
├─────────────────────────────────────────────────────────────────┤
│ Input:                                                           │
│   • System prompt: "Keep refining..."                           │
│   • refinement-0001.md (for context)                            │
│   • refinement-0002.md (latest)                                 │
│   • (NO input files)                                            │
│                                                                  │
│ Output:                                                          │
│   → refinement-0003.md                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ ITERATIONS 4-10: Continue Refinement                            │
├─────────────────────────────────────────────────────────────────┤
│ Each iteration:                                                  │
│   • System prompt: "Keep refining..."                           │
│   • Last 2 refinements ONLY                                     │
│   • NO input files                                              │
│   • KB/RAG (top 3 chunks from vector DB)                        │
│                                                                  │
│ Iterations produce:                                              │
│   → refinement-0004.md                                          │
│   → refinement-0005.md                                          │
│   → ...                                                          │
│   → refinement-0010.md                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌═════════════════════════════════════════════════════════════════┐
║ ITERATION 11: SPECIAL EVALUATION LOOP (every 10th)              ║
╠═════════════════════════════════════════════════════════════════╣
║ Input:                                                           ║
║   • Original user prompt (from iteration 1)                     ║
║   • ALL input files (from /input folder)                        ║
║   • Latest refinement (refinement-0010.md)                      ║
║                                                                  ║
║ AI Process - Comparison & Evaluation:                           ║
║   ┌───────────────────────────────────────┐                    ║
║   │ Compare:                               │                    ║
║   │ "Did AI achieve the objective?"       │                    ║
║   │ "How close to user's input files?"    │                    ║
║   │ "What's missing?"                      │                    ║
║   │                                        │                    ║
║   │ Scores:                                │                    ║
║   │ • Objective Alignment: 7/10            │                    ║
║   │ • Completeness: 6/10                   │                    ║
║   │ • Input Alignment: 5/10                │                    ║
║   │ • Progress: 65%                        │                    ║
║   │                                        │                    ║
║   │ Identifies:                            │                    ║
║   │ • Gaps to fill                         │                    ║
║   │ • Strengths to keep                    │                    ║
║   │ • Recommendations                      │                    ║
║   └───────────────────────────────────────┘                    ║
║                                                                  ║
║ Output:                                                          ║
║   → report/report-0001.md                                       ║
╚═════════════════════════════════════════════════════════════════╝
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ ITERATION 12: Back to Regular Refinement                        │
├─────────────────────────────────────────────────────────────────┤
│ Input:                                                           │
│   • System prompt: "Keep refining..."                           │
│   • refinement-0010.md                                          │
│   • refinement-0011.md                                          │
│   • (NO input files - just like iterations 2-10)               │
│                                                                  │
│ Output:                                                          │
│   → refinement-0012.md                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ ITERATIONS 13-20: Regular Refinement                            │
├─────────────────────────────────────────────────────────────────┤
│ Each iteration: System prompt + last 2 refinements              │
│ NO input files                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌═════════════════════════════════════════════════════════════════┐
║ ITERATION 21: EVALUATION LOOP #2 (every 10th)                  ║
╠═════════════════════════════════════════════════════════════════╣
║ Input:                                                           ║
║   • Original prompt + input files + refinement-0020.md          ║
║                                                                  ║
║ Output:                                                          ║
║   → report/report-0002.md                                       ║
║     "Progress: 85% (improved from 65%!)"                        ║
╚═════════════════════════════════════════════════════════════════╝
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ ITERATIONS 22-30: Regular Refinement                            │
│ (System prompt + last 2 refinements, NO input files)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌═════════════════════════════════════════════════════════════════┐
║ ITERATION 31: EVALUATION LOOP #3                                ║
║   → report/report-0003.md: "Progress: 95%"                      ║
╚═════════════════════════════════════════════════════════════════╝
                              ↓
                    ... continues infinitely ...
```

## Key Points

### ✅ Input Files Used ONLY In:
1. **Iteration 1** (Initial research)
2. **Evaluation loops** (iterations 11, 21, 31, 41...)

### ❌ Input Files NOT Used In:
- **Regular refinements** (iterations 2-10, 12-20, 22-30, etc.)

### Why This Makes Sense

**Regular Refinement (iterations 2-10, 12-20, etc.):**
```
Goal: Improve the document itself
Input: Last 2 refinements
Task: "Make this better, add depth, fix issues"
Result: Incremental improvements

→ No need for input files (already saw them in iteration 1)
→ Just polishing what exists
```

**Evaluation Loop (iterations 11, 21, 31, etc.):**
```
Goal: Compare against original objective
Input: Original prompt + input files + latest refinement
Task: "How well did AI achieve the objective?"
Result: Progress report with scores

→ NEED input files to compare
→ "Did AI learn what user wanted?"
```

## Context Window Usage

### Iteration 1 (Initial)
```
Context:
  • User prompt:        ~200 tokens
  • Input files:        ~1000 tokens
  • AI instructions:    ~300 tokens
  ────────────────────────────────
  Total:               ~1500 tokens ✓
```

### Iterations 2-10 (Regular Refinement)
```
Context:
  • System prompt:       ~200 tokens
  • refinement-(N-2):    ~1000 tokens
  • refinement-(N-1):    ~1000 tokens
  • KB/RAG top-3:        ~500 tokens
  ────────────────────────────────
  Total:                ~2700 tokens ✓
```

### Iteration 11 (Evaluation)
```
Context:
  • Original prompt:     ~200 tokens
  • Input files:         ~1000 tokens
  • Latest refinement:   ~1000 tokens (truncated)
  • Evaluation task:     ~500 tokens
  ────────────────────────────────
  Total:                ~2700 tokens ✓
```

**All fit comfortably in weak model's 4K context!**

## Detailed Iteration Breakdown

```
┌──────────┬─────────────┬──────────────────────┬─────────────┐
│ Iteration│ Type        │ Context              │ Output      │
├──────────┼─────────────┼──────────────────────┼─────────────┤
│    1     │ Initial     │ Prompt + Input files │ ref-0001.md │
│    2     │ Refine      │ Sys prompt + 0001    │ ref-0002.md │
│    3     │ Refine      │ Sys prompt + 0001,02 │ ref-0003.md │
│    4     │ Refine      │ Sys prompt + 0002,03 │ ref-0004.md │
│   ...    │ ...         │ ...                  │ ...         │
│   10     │ Refine      │ Sys prompt + 0008,09 │ ref-0010.md │
├──────────┼─────────────┼──────────────────────┼─────────────┤
│   11     │ EVALUATION  │ Prompt + Input + 0010│ report-01.md│
├──────────┼─────────────┼──────────────────────┼─────────────┤
│   12     │ Refine      │ Sys prompt + 0010,11 │ ref-0012.md │
│   13     │ Refine      │ Sys prompt + 0011,12 │ ref-0013.md │
│   ...    │ ...         │ ...                  │ ...         │
│   20     │ Refine      │ Sys prompt + 0018,19 │ ref-0020.md │
├──────────┼─────────────┼──────────────────────┼─────────────┤
│   21     │ EVALUATION  │ Prompt + Input + 0020│ report-02.md│
├──────────┼─────────────┼──────────────────────┼─────────────┤
│   22     │ Refine      │ Sys prompt + 0020,21 │ ref-0022.md │
│   ...    │ ...         │ ...                  │ ...         │
└──────────┴─────────────┴──────────────────────┴─────────────┘
```

## What Each Prompt Says

### Iteration 1 (Initial Research)
```
User's Original Prompt:
"Research quantum computing with focus on NISQ algorithms"

Input Files:
[Content of user's PDF, notes, etc.]

AI Task:
"Conduct comprehensive research on this topic, using the provided
materials as context."
```

### Iterations 2-10, 12-20, etc. (Regular Refinement)
```
System Refinement Prompt:
"Refine and improve the research document. Search for more depth,
add recent developments, fill gaps, improve clarity."

Previous Refinements:
refinement-0001.md
refinement-0002.md  (only last 2)

AI Task:
"Make this document better through web research and analysis."
```

**Note:** System prompt is the same every time. AI just keeps improving the document.

### Iterations 11, 21, 31, etc. (Evaluation)
```
Evaluation Prompt:
"Compare the current research against the original objective."

Original User Prompt:
"Research quantum computing with focus on NISQ algorithms"

Input Files:
[User's PDF, notes, etc.]

Latest Refinement:
refinement-0010.md

AI Task:
"How well did the research achieve the objective? Score alignment,
completeness, identify gaps."
```

## Why Input Files Only in Iteration 1 & Evaluations

### ✅ Iteration 1 (Initial)
**Needs input files:**
- Sets the research direction
- Provides user's domain knowledge
- Gives context for what to research

### ✅ Evaluations (11, 21, 31...)
**Needs input files:**
- Compare: "Did AI learn what user wanted?"
- Check: "Is research aligned with user's materials?"
- Measure: Progress toward user's objective

### ❌ Iterations 2-10, 12-20, etc. (Regular Refinement)
**Doesn't need input files:**
- Just improving the existing document
- Searching web for more info
- Making incremental improvements
- Input files already influenced iteration 1

**Including them would:**
- ❌ Waste context window
- ❌ Redundant (already saw in iteration 1)
- ❌ No new information
- ❌ Just refining existing doc, not starting over

## Timeline Example

```
Iteration 1 (Initial):
  📁 Input: User prompt + user_notes.pdf + data.csv
  🔍 AI: Researches quantum computing
  💾 Output: refinement-0001.md (3000 chars)

Iteration 2 (Refine):
  📝 Input: "Keep refining" + refinement-0001.md
  🔍 AI: Searches for more depth on quantum algorithms
  💾 Output: refinement-0002.md (3500 chars, improved!)

Iteration 3 (Refine):
  📝 Input: "Keep refining" + ref-0001.md + ref-0002.md
  🔍 AI: Adds recent 2025 developments
  💾 Output: refinement-0003.md (4000 chars)

...iterations 4-10 continue same pattern...

Iteration 11 (EVALUATION):
  📊 Input: Original prompt + user_notes.pdf + data.csv + ref-0010.md
  🎯 AI: Compares research vs objective
  📋 Output: report/report-0001.md
    ├─ Objective Alignment: 7/10
    ├─ Completeness: 6/10
    ├─ Input Alignment: 5/10
    ├─ Gaps: Missing X, Y, Z
    └─ Progress: 65%

Iteration 12 (Refine):
  📝 Input: "Keep refining" + ref-0010.md + ref-0011.md
  (NO input files - back to regular refinement)
  💾 Output: refinement-0012.md

...iterations 13-20...

Iteration 21 (EVALUATION):
  📊 Input: Original prompt + input files + ref-0020.md
  📋 Output: report/report-0002.md
    └─ Progress: 85% (improved from 65%!)

...repeat infinitely...
```

## Context Window Breakdown

### Iteration 1
```
User prompt:             200 tokens
Input files (all):      1000 tokens
Research instructions:   300 tokens
─────────────────────────────────
Total:                  1500 tokens
```

### Iterations 2-10 (Regular)
```
System prompt:           200 tokens
refinement-(N-2).md:    1000 tokens
refinement-(N-1).md:    1000 tokens
KB/RAG top-3:            500 tokens
─────────────────────────────────
Total:                  2700 tokens
```

### Iteration 11 (Evaluation)
```
Original prompt:         200 tokens
Input files:            1000 tokens
Latest refinement:      1000 tokens (truncated)
Evaluation task:         500 tokens
─────────────────────────────────
Total:                  2700 tokens
```

**All under 4K for weak models!**

## Benefits of This Approach

### Memory Efficiency
✓ Input files used only when needed
✓ Regular iterations: ~2700 tokens
✓ No context waste

### Learning Strategy
✓ Iteration 1: AI learns with user's guidance
✓ Iterations 2-10: AI improves independently
✓ Iteration 11: Check if AI learned correctly
✓ Iterations 12-20: Continue improving
✓ Iteration 21: Check progress again

### Weak Model Optimization
✓ Minimal context every iteration
✓ No redundant information
✓ Focused prompts
✓ Clear task separation

## File Usage Summary

```
/input folder:
  ├── user_notes.pdf
  └── data.csv

Used in:
  ✓ Iteration 1 (initial research)
  ✓ Iteration 11 (evaluation)
  ✓ Iteration 21 (evaluation)
  ✓ Iteration 31 (evaluation)
  ...

NOT used in:
  ✗ Iterations 2-10 (regular refinement)
  ✗ Iterations 12-20 (regular refinement)
  ✗ Iterations 22-30 (regular refinement)
  ...

Why: Input files set the objective. Regular refinements just improve
the document. Evaluations check progress against objective.
```

## The Old "Delayed Input" Concept - REMOVED

~~**Old idea:** Add input files after iteration 10~~
~~**Problem:** Would affect ALL subsequent iterations unnecessarily~~

**New approach:** Input files only in:
- Iteration 1 (initial)
- Evaluation loops (every 10th)

**Better because:**
- Cleaner separation of concerns
- More efficient context usage
- Input files = objective/baseline
- Refinements = iterative improvement
- Evaluations = progress check

## Updated Code Behavior

The code now:

1. **Iteration 1:** Uses input files to guide initial research
2. **Iterations 2-N:** System refinement prompt + last 2 refinements only
3. **Every 10th iteration:** Evaluation with original prompt + input files + latest refinement

**Input files are NEVER added to regular refinement context.**

They're only for:
- Setting initial direction
- Evaluation comparisons

---

**Does this flow make sense?** This is much cleaner than the "delayed unlock" approach! 🎯
