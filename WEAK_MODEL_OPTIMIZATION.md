## Weak Model Optimization Strategy

This system is optimized for **weak/small models** (7B-13B parameters) that have limited context windows and may struggle with long conversation histories.

## The Problem

Weak models face challenges:
- **Limited context window** (4K-8K tokens)
- **Context degradation** with long conversations
- **Slow inference** on consumer hardware
- **Quality degrades** with too much input

## Our Solution: Iterative Learning Loop

Instead of maintaining long conversation history, we use **short-term context + long-term memory**:

```
┌──────────────────────────────────────────────────────┐
│  Short-Term Context (Each Iteration)                 │
│  ────────────────────────────────────────            │
│  • Last 2 refinement files only                      │
│  • User input files (optional)                       │
│  • Search terms from previous iteration              │
│  • Identified research gaps                          │
│  Total: ~2000-4000 tokens                           │
└──────────────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────┐
│  Long-Term Memory (Accumulated Knowledge)            │
│  ────────────────────────────────────────────        │
│  • Vector Database (RAG)                             │
│  • Knowledge Base (KB)                               │
│  • Search term history                               │
│  Retrieved on-demand: ~500-1000 tokens              │
└──────────────────────────────────────────────────────┘
```

## Architecture

### 1. Input File Selection

**Before each research session:**

```
User starts script
     ↓
Script shows input files from ./input folder
     ↓
User selects: 0 (none), 1 (all), 2-N (specific files)
     ↓
Selected files copied to /generation/research-id/input
     ↓
Files read and formatted for AI context
```

**Benefits:**
- User provides domain knowledge
- Files included in ALL iterations
- Weak model gets consistent context

### 2. Refinement File Format

**Each refinement includes metadata at the top:**

```markdown
<!-- RESEARCH_ID: research-20250121-143022 -->
<!-- VERSION: 0003 -->
<!-- SEARCH_TERMS: quantum computing basics, quantum algorithms NISQ, quantum hardware qubits -->

---

# Research Document Title

[... actual content ...]
```

**Why this matters:**
- Next iteration reads search terms
- AI learns what was searched before
- Avoids redundant searches
- Enables search variation strategy

### 3. Context Management Strategy

**Each refinement iteration uses:**

```
Iteration N receives:
├── Input Files (user-provided, consistent across all iterations)
├── Refinement N-1 (most recent, full content)
├── Refinement N-2 (previous, full content)
├── Search Terms (from N-1)
├── Identified Gaps (auto-detected from N-1, N-2)
└── Vector DB Context (top 3 relevant chunks)
```

**What we DON'T send:**
- ❌ Refinements 1 through N-3 (too old)
- ❌ Full conversation history
- ❌ Agent messages and tool calls
- ❌ Duplicate context

**Total context per iteration:**
- User files: ~1000 tokens
- Last 2 refinements: ~2000 tokens (truncated if longer)
- Instructions + gaps: ~500 tokens
- Vector context: ~500 tokens
- **Total: ~4000 tokens** ✅ Fits in weak model!

### 4. Iterative Learning Loop

```
Iteration 1:
  Input: User prompt + input files
  Searches: ["topic basics", "topic history", "topic applications", ...]
  Output: refinement-0001.md (with search terms)
  KB Update: Add to vector DB + knowledge base

Iteration 2:
  Input: refinement-0001.md + input files
  Learns: Reads search terms from 0001
  Searches: ["topic basics detailed", "topic recent 2025", ...]
  Output: refinement-0002.md (with new search terms)
  KB Update: Add to vector DB + knowledge base

Iteration 3:
  Input: refinement-0001.md + refinement-0002.md + input files
  Learns: Reads search terms from 0002, compares with 0001
  Identifies Gaps: "Section X is short", "Missing case studies"
  Searches: ["topic case studies examples", "topic X detailed", ...]
  Output: refinement-0003.md (with evolved search terms)
  KB Update: Add to vector DB + knowledge base

Iteration N:
  Input: refinement-(N-2).md + refinement-(N-1).md + input files
  Learns: Evolution of search terms, identified gaps
  Searches: Increasingly specific, targeted queries
  Output: refinement-NNNN.md
  Loop continues infinitely...
```

### 5. Search Term Evolution

**Generation Strategy:**

```python
Iteration 1 (Cold Start):
  base_topic = "quantum computing"
  searches = [
    "quantum computing overview basics",
    "quantum computing history background",
    "quantum computing current state recent",
    "quantum computing applications uses",
    "quantum computing challenges limitations",
    "quantum computing future trends prospects"
  ]

Iteration 2 (Learning):
  previous_terms = ["quantum computing basics", ...]
  searches = [
    "quantum computing basics detailed analysis",
    "quantum computing basics recent developments 2025",
    "quantum computing basics case studies examples"
  ]

Iteration 3+ (Deepening):
  previous_terms = ["quantum basics detailed", ...]
  gaps = ["Expand section: Hardware Implementation"]
  searches = [
    "quantum hardware qubits implementation",
    "quantum hardware error correction",
    "quantum hardware recent breakthroughs 2025"
  ]
```

**Benefits:**
- Searches become more specific over time
- Avoids redundant searches
- Fills identified gaps
- Natural progression from broad to deep

### 6. Gap Identification

**Automatic gap detection:**

```python
def extract_research_gaps(refinements):
    gaps = []

    # 1. Find TODO/FIXME markers
    if "TODO: Add examples" in content:
        gaps.append("Add concrete examples")

    # 2. Find short sections
    if section_length < 200 chars:
        gaps.append(f"Expand section: {section_title}")

    # 3. Missing subsections (heuristic)
    if "## Applications" exists but no subsections:
        gaps.append("Add application examples")

    return gaps
```

**Used for refinement:**
```
Next iteration gets:
  "Identified Gaps to Address:"
  - Expand section: Hardware Implementation
  - Add concrete case studies
  - Update with recent 2025 developments
```

## File Organization

```
input/                              ← User places files here
  ├── research_paper.pdf
  ├── notes.txt
  └── data.csv

generation/
  └── research-20250121-143022/
      ├── input/                   ← Copied from above
      │   ├── research_paper.pdf
      │   ├── notes.txt
      │   └── data.csv
      ├── refinement-0001.md       ← With metadata
      ├── refinement-0002.md       ← With evolved search terms
      ├── refinement-NNNN.md       ← Latest
      ├── rag/
      │   └── vectors.db           ← All refinements chunked
      └── kb/
          ├── knowledge.db         ← Knowledge base
          └── metadata.json
```

## Why This Works for Weak Models

### 1. **Minimal Context Window**
- Only last 2 refinements = ~2000 tokens
- Fits easily in 4K-8K context windows
- No context overflow errors

### 2. **No Context Degradation**
- Each iteration starts fresh
- No accumulated garbage from long conversations
- Clean, focused prompts

### 3. **Iterative Improvement**
- Small improvements each iteration
- Weak model can handle incremental changes
- Quality compounds over time

### 4. **External Memory**
- Vector DB stores ALL previous work
- Retrieved only when needed
- Model doesn't need to "remember" everything

### 5. **Guided Search Evolution**
- AI learns from search terms in previous files
- Don't need to "figure out" what to search
- Previous iterations teach current iteration

## Performance Characteristics

### Context Usage Per Iteration

```
Component                 | Tokens | % of 4K Context
──────────────────────────|────────|─────────────────
Input files               | ~1000  | 25%
Last 2 refinements        | ~2000  | 50%
Instructions + gaps       | ~500   | 12.5%
Vector DB context         | ~500   | 12.5%
──────────────────────────|────────|─────────────────
TOTAL                     | ~4000  | 100%
```

### Memory Over Time

```
Iterations | Context Window | Vector DB Size | KB Size
───────────|─────────────────|────────────────|─────────
1          | 4K tokens      | 10 chunks      | 5 KB
5          | 4K tokens      | 50 chunks      | 25 KB
10         | 4K tokens      | 100 chunks     | 50 KB
50         | 4K tokens      | 500 chunks     | 250 KB
100        | 4K tokens      | 1000 chunks    | 500 KB
```

**Notice:** Context window stays constant while knowledge grows!

### Typical Iteration Performance

```
7B Model (e.g., Llama-3.1-7B):
  - Iteration time: 2-3 minutes
  - Context: 4000 tokens
  - Output: 500-1000 tokens
  - Searches: 3-5 parallel queries

13B Model (e.g., Llama-3.1-13B):
  - Iteration time: 3-5 minutes
  - Context: 4000 tokens
  - Output: 1000-2000 tokens
  - Searches: 5-7 parallel queries
```

## Example: Full Research Session

```bash
$ python research_orchestrator.py "Quantum Computing"

=== Input File Selection ===
Available files:
  2. quantum_paper.pdf (2.3 MB)
  3. notes.txt (15 KB)
Select: 2,3
✓ Selected 2 files

=== Phase 1: Initial Research ===
✓ Executing 6 parallel searches...
✓ Saved refinement-0001.md
  Search terms: quantum basics, quantum algorithms, ...

=== Phase 2: Infinite Refinement ===
Context: Last 2 refinements + KB/RAG

Iteration 1→2:
  ├─ Loaded: refinement-0001.md
  ├─ Previous searches: quantum basics, quantum algorithms, ...
  ├─ New searches: quantum basics detailed, quantum algorithms NISQ recent, ...
  └─ Saved: refinement-0002.md

Iteration 2→3:
  ├─ Loaded: refinement-0001.md, refinement-0002.md
  ├─ Previous searches: quantum basics detailed, ...
  ├─ Identified gaps: Expand section: Hardware Implementation
  ├─ New searches: quantum hardware implementation, quantum error correction, ...
  └─ Saved: refinement-0003.md

[Continues infinitely until Ctrl+C]
```

## Configuration for Weak Models

```yaml
# config.yaml
lmstudio:
  model: "llama-3.1-7b-instruct"  # 7B model
  temperature: 0.7
  max_tokens: 2048               # Reduced for weak models

research:
  refinement_delay: 15           # More time between iterations

vector_db:
  chunk_size: 512                # Smaller chunks

# In agents/research_agent.py:
parallel_search = ParallelDuckDuckGoSearch(
    max_results_per_query=3,     # Fewer results = less to process
    timeout=15                   # More time per search
)
```

## Tips for Best Results

1. **Start Broad, Go Deep**
   - First iteration: Overview
   - Later iterations: Specific details

2. **Use Input Files Wisely**
   - Include domain knowledge
   - Keep files concise (<10 pages)
   - Text files work best

3. **Let It Run**
   - 5-10 iterations minimum
   - Quality improves gradually
   - Don't interrupt too early

4. **Monitor Context**
   - Check log for "context too long" warnings
   - Reduce input files if needed
   - Increase refinement_delay if model struggles

5. **Search Evolution**
   - Trust the search term learning
   - Terms become more specific naturally
   - Gaps filled automatically

## Comparison: Weak vs Strong Models

| Aspect | Strong Model (70B+) | Weak Model (7B-13B) |
|--------|---------------------|---------------------|
| **Context Window** | 32K-128K tokens | 4K-8K tokens |
| **Strategy** | Full conversation history | Last 2 refs + KB/RAG |
| **Iteration Time** | 30s-1min | 2-5min |
| **Quality/Iteration** | High | Moderate |
| **Total Iterations** | 5-10 needed | 10-20 needed |
| **Final Quality** | ★★★★★ | ★★★★☆ |
| **Cost** | High (GPU req'd) | Low (CPU possible) |

## Conclusion

This optimization strategy enables **weak models to produce high-quality research** through:

✓ **Short context** (no overflow)
✓ **Iterative learning** (compounds over time)
✓ **External memory** (vector DB + KB)
✓ **Search evolution** (learns from previous)
✓ **Gap filling** (auto-detected)
✓ **User guidance** (input files)

**Result:** A 7B model can produce research comparable to larger models, just takes more iterations!

---

**Perfect for:** Consumer hardware, local models, privacy-focused research, cost-sensitive applications
