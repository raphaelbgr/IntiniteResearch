# Complete Usage Guide

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure LMStudio
# Edit config.yaml with your model name

# 3. (Optional) Place input files in ./input folder

# 4. Run research
python research_orchestrator.py "Your research topic"

# 5. Select input files when prompted
# - 0: No files
# - 1: All files
# - 2-N: Specific files

# 6. Watch it work!
# - Initial research with parallel searches
# - Infinite refinement with learning
# - Press Ctrl+C when satisfied
```

## Input File System

### Purpose

Provide the AI with:
- Domain knowledge
- Reference materials
- Data to analyze
- Context for research

### Setup

1. **Create input directory** (if not exists):
```bash
mkdir input
```

2. **Add your files**:
```bash
input/
  ├── research_paper.pdf
  ├── notes.txt
  ├── data.csv
  └── context.md
```

### Supported File Types

- **Text**: `.txt`, `.md`
- **Documents**: `.pdf` (text extracted)
- **Data**: `.json`, `.csv`, `.xml`
- **Code**: `.py`, `.js`, `.java`, etc.
- **HTML**: `.html`

Binary files are noted but not read.

### Selection Process

**When you start research:**

```
╔════════════════════════════════════╗
║  Input File Selection              ║
╚════════════════════════════════════╝

Available Input Files:

ID  Filename            Size    Type
──  ────────────────   ──────   ─────
2   research_paper.pdf 2.3 MB   PDF
3   notes.txt          15 KB    TXT
4   data.csv           45 KB    CSV

Options:
  0 - No input files (prompt only)
  1 - ALL files
  2-4 - Specific file from list
  2,3,4 - Multiple files (comma-separated)

Select files (default: 0): 2,3
✓ Selected 2 file(s):
  • research_paper.pdf
  • notes.txt
```

### How Files Are Used

**Copied to research session:**
```
generation/research-XXXXX/input/
  ├── research_paper.pdf (copy)
  └── notes.txt (copy)
```

**Included in every iteration:**
- Initial research (refinement-0001.md)
- Refinement #2 (refinement-0002.md)
- Refinement #N (refinement-NNNN.md)
- All iterations have consistent file context

**Format in prompt:**
```markdown
# Input Files Provided by User

## File: research_paper.pdf

[... PDF content extracted as text ...]

## File: notes.txt

[... notes content ...]

---

[Your research prompt here]
```

## Refinement File Format

Each refinement includes metadata:

```markdown
<!-- RESEARCH_ID: research-20250121-143022 -->
<!-- VERSION: 0003 -->
<!-- SEARCH_TERMS: quantum computing hardware, quantum error correction, quantum algorithms NISQ -->

---

# Quantum Computing Research

## Executive Summary
...
```

**Metadata fields:**
- `RESEARCH_ID`: Unique session identifier
- `VERSION`: Refinement number (0001, 0002, ...)
- `SEARCH_TERMS`: Comma-separated search queries used

**Why metadata matters:**
- Next iteration reads search terms
- Learns what was searched before
- Enables search variation strategy
- Avoids redundant searches

## Iteration Flow

### Initial Research (Version 1)

```
User Input:
  ├─ Research topic
  └─ Optional input files

AI Process:
  1. Analyzes topic
  2. Breaks into 5-7 key aspects
  3. Executes parallel DuckDuckGo searches
  4. Synthesizes results

Output:
  └─ refinement-0001.md (with search terms)
```

### Refinement Loop (Version 2+)

```
Context Loaded:
  ├─ Input files (if any)
  ├─ refinement-(N-2).md
  ├─ refinement-(N-1).md
  ├─ Search terms from (N-1)
  ├─ Identified gaps
  └─ Vector DB context (top 3)

AI Process:
  1. Reviews last 2 refinements
  2. Extracts previous search terms
  3. Identifies gaps/weaknesses
  4. Generates evolved search terms
  5. Executes new parallel searches
  6. Refines document

Output:
  └─ refinement-NNNN.md (with new search terms)
```

### Search Term Evolution

**Example progression:**

```
Version 1:
  - quantum computing overview basics
  - quantum computing history background
  - quantum computing current state

Version 2:
  - quantum computing overview basics detailed analysis
  - quantum computing history background recent developments
  - quantum computing current state 2025

Version 3:
  - quantum hardware implementation specifics
  - quantum error correction techniques
  - quantum algorithms NISQ era

Version N:
  - [Increasingly specific based on gaps]
  - [Targeted recent developments]
  - [Deep technical details]
```

## Context Window Management

### Problem: Weak Models

7B-13B models typically have:
- 4K-8K token context windows
- Performance degrades with long contexts
- Can't handle full conversation history

### Solution: Last 2 Refinements Only

```
┌────────────────────────────────────┐
│  Iteration N Context              │
├────────────────────────────────────┤
│  • Input files        ~1000 tokens│
│  • Refinement (N-2)   ~1000 tokens│
│  • Refinement (N-1)   ~1000 tokens│
│  • Instructions       ~500 tokens │
│  • Vector context     ~500 tokens │
├────────────────────────────────────┤
│  TOTAL:              ~4000 tokens │
└────────────────────────────────────┘

✓ Fits in 4K-8K context windows
✓ No overflow errors
✓ Consistent performance
```

### What About Older Refinements?

**Stored in vector database:**
- All refinements chunked and embedded
- Retrieved on-demand (top 3 chunks)
- AI can access relevant historical content
- Without overwhelming context

**Example:**

```
Version 10 iteration:
  Direct context:
    - refinement-0008.md (full)
    - refinement-0009.md (full)

  Vector DB provides:
    - Chunk from 0003: "Hardware section"
    - Chunk from 0005: "Algorithm details"
    - Chunk from 0007: "Recent developments"

Result: AI has full recent context + relevant history!
```

## Gap Identification

Automatically detects weaknesses:

### 1. TODO/FIXME Markers

```markdown
## Applications

TODO: Add real-world case studies

## Hardware

FIXME: Update with 2025 developments
```

**Detected gaps:**
- "Add real-world case studies"
- "Update with 2025 developments"

### 2. Short Sections

```markdown
## Quantum Algorithms

Brief overview here. (Only 150 characters!)

## Quantum Hardware

Detailed section with multiple paragraphs...
```

**Detected gap:**
- "Expand section: Quantum Algorithms"

### 3. Missing Examples

Heuristics detect:
- Sections without subsections
- Claims without evidence
- Technical terms without explanation

## Complete Example Session

```bash
$ python research_orchestrator.py "Climate Change Adaptation Strategies"

╔════════════════════════════════════════════════════════╗
║ Infinite Research Refinement System                   ║
║ with Parallel DuckDuckGo Search (1-10 queries)        ║
║ Optimized for Weak Models: Last 2 refinements + KB/RAG║
╚════════════════════════════════════════════════════════╝

Initializing research: Climate Change Adaptation Strategies...

╔═══ Input File Selection ═══╗

Available Input Files:

ID  Filename         Size    Type
──  ───────────────  ──────  ────
2   ipcc_report.pdf  5.2 MB  PDF
3   notes.txt        8 KB    TXT
4   data.csv         12 KB   CSV

Options:
  0 - No input files (prompt only)
  1 - ALL files
  2-4 - Specific file from list

Select files (default: 0): 2,3
✓ Selected 2 file(s):
  • ipcc_report.pdf
  • notes.txt

Research ID: research-20250121-143528
✓ Copied 2 input file(s) to session

══════════════════════════════════════════
Phase 1: Initial Research with Parallel Search
══════════════════════════════════════════
Agent will use parallel DuckDuckGo search (1-10 queries)

[INFO] Agent analyzing topic...
[INFO] Executing 6 parallel searches...
  - climate change adaptation overview
  - climate adaptation strategies agriculture
  - climate adaptation infrastructure
  - climate adaptation policy frameworks
  - climate adaptation technology solutions
  - climate adaptation challenges barriers

[INFO] Aggregating 30 search results...
[INFO] Synthesizing research document...
[INFO] Saved refinement-0001.md (2,547 characters)
[INFO] Search terms used: climate change adaptation overview, ...

══════════════════════════════════════════
Phase 2: Infinite Refinement Loop
══════════════════════════════════════════
Context Strategy: Last 2 refinements + KB/RAG
Learning: Search variations improve each iteration
══════════════════════════════════════════

Starting infinite refinement loop (optimized for weak models)
Press Ctrl+C to stop

[INFO] Refinement 1 → 2
[INFO] Loaded 1 previous refinement
[INFO] Previous searches: climate change adaptation overview, ...
[INFO] Generated 7 search variations
[INFO] Identified gaps:
  - Expand section: Agricultural Adaptation
  - Add recent 2025 developments
[INFO] Executing 7 parallel searches...
[INFO] Saved refinement-0002.md (3,892 characters)
[INFO] Refinement 2 complete. Waiting 10s...

[INFO] Refinement 2 → 3
[INFO] Loaded 2 previous refinements
[INFO] Previous searches: climate adaptation detailed, ...
[INFO] Generated 7 search variations
[INFO] Identified gaps:
  - Add concrete case studies
[INFO] Executing 7 parallel searches...
[INFO] Saved refinement-0003.md (4,521 characters)
[INFO] Refinement 3 complete. Waiting 10s...

[... continues infinitely until Ctrl+C ...]

^C
Received interrupt signal...
Stopping refinement loop...
Refinement loop stopped at version 12

Cleaning up...
Research session saved: generation/research-20250121-143528

Final session:
  - Refinements: 12 versions
  - Input files: 2
  - Vector chunks: 156
  - Knowledge base: Updated

✓ Complete
```

## Output Structure

```
generation/research-20250121-143528/
  ├── input/                      # Copied input files
  │   ├── ipcc_report.pdf
  │   └── notes.txt
  │
  ├── refinement-0001.md         # Initial research
  ├── refinement-0002.md         # First refinement
  ├── refinement-0003.md         # Second refinement
  ├── ...
  ├── refinement-0012.md         # Latest (stopped at 12)
  │
  ├── rag/
  │   └── vectors.db            # Vector embeddings (all versions)
  │
  ├── kb/
  │   ├── knowledge.db          # Knowledge base
  │   ├── knowledge.txt         # Text knowledge
  │   └── metadata.json         # Session metadata
  │
  ├── memory/
  │   └── agent_memory.db       # Agent conversation history
  │
  └── logs/
      └── research.log          # Detailed execution logs
```

## Tips & Best Practices

### For Input Files

✓ **DO:**
- Use relevant domain knowledge
- Include concise reference materials
- Provide structured data (CSV, JSON)
- Keep files under 10 MB each

✗ **DON'T:**
- Upload entire books (too much context)
- Include irrelevant files
- Use corrupted/broken files

### For Weak Models

✓ **DO:**
- Let it run for 10-20 iterations
- Use refinement_delay: 15-30 seconds
- Reduce max_results_per_query to 3-5
- Monitor logs for "context too long" warnings

✗ **DON'T:**
- Interrupt too early (< 5 iterations)
- Use files > 10 MB
- Set refinement_delay < 10 seconds

### For Strong Models

✓ **CAN:**
- Reduce refinement_delay to 5 seconds
- Increase max_results_per_query to 10
- Use larger input files (20-50 MB)
- Achieve good results in 5-10 iterations

## Monitoring Progress

### Check Latest Version

```bash
# Linux/Mac
cat generation/research-*/refinement-*.md | tail -1

# Windows
type generation\research-*\refinement-*.md
```

### View Search Terms Evolution

```bash
# Extract search terms from all refinements
grep "SEARCH_TERMS" generation/research-20250121-*/refinement-*.md
```

### Check Vector DB Size

```bash
# Linux/Mac
ls -lh generation/research-*/rag/vectors.db

# Windows
dir generation\research-*\rag\vectors.db
```

### Monitor Logs

```bash
tail -f research.log
```

## Troubleshooting

### "Context too long" errors

**Solution:**
1. Reduce input file sizes
2. Increase max_tokens in config.yaml
3. Use a model with larger context window

### Refinements not improving

**Solution:**
1. Let it run longer (15-20 iterations)
2. Check if search terms are evolving (grep SEARCH_TERMS)
3. Verify web search is working (check logs)

### Out of memory

**Solution:**
1. Close other applications
2. Reduce num parallel searches
3. Use smaller model (7B instead of 13B)
4. Increase refinement_delay

### Poor quality output

**Solution:**
1. Provide better input files with domain knowledge
2. Use more specific research topic
3. Let it run more iterations
4. Check if model supports instruction following

## Advanced: Resuming Research

Currently, each run is independent. To resume:

1. **Manual approach:**
   - Copy last 2 refinements to new session
   - Start new research with same topic
   - Add as input files

2. **Programmatic** (advanced):
```python
from storage.file_manager import FileManager
from refinement.refiner import RefinementEngine

fm = FileManager()
sessions = fm.list_research_sessions()
# Pick session and continue...
```

## Next Steps

- Read [WEAK_MODEL_OPTIMIZATION.md](WEAK_MODEL_OPTIMIZATION.md) for strategy details
- Read [PARALLEL_SEARCH_GUIDE.md](PARALLEL_SEARCH_GUIDE.md) for search tool info
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [QUICKSTART.md](QUICKSTART.md) for 5-minute setup

---

Happy researching! 🔬📚
