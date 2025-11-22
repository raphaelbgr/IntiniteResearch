# Quick Start Guide

Get up and running with Infinite Research in 5 minutes!

## Step 1: Prerequisites

Ensure you have:
- Python 3.10 or higher
- LMStudio installed and running

## Step 2: Setup LMStudio

1. **Open LMStudio**
2. **Download a model** (if you haven't already)
   - Recommended: `llama-3.1-8b-instruct` or similar
3. **Load the model**
4. **Start the server**
   - Click the server icon
   - Keep default settings (port 1234)
   - Click "Start Server"
5. **Note your model name** displayed in LMStudio

## Step 3: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure

Edit `config.yaml`:

```yaml
lmstudio:
  base_url: "http://localhost:1234/v1"
  model: "llama-3.1-8b-instruct"  # ← Your model name here
  temperature: 0.7
  max_tokens: 4096
```

## Step 5: Run Your First Research

```bash
python research_orchestrator.py "What are the latest developments in quantum computing?"
```

## What You'll See

```
======================================================================
Infinite Research Refinement System
======================================================================
[INFO] Initializing research: What are the latest developments in quantum computing?
[INFO] Research ID: research-20250121-143022
[INFO] Created research directory: generation/research-20250121-143022
======================================================================
Phase 1: Initial Parallel Research
======================================================================
[INFO] Starting parallel research on: What are the latest developments in quantum computing?
[INFO] Decomposed into 5 subtopics
...
[INFO] Initial research completed and saved as refinement-0001.md
======================================================================
Phase 2: Infinite Refinement Loop
======================================================================
[INFO] Starting infinite refinement loop
[INFO] Refinement delay: 10 seconds
[INFO] Press Ctrl+C to stop
[INFO] Starting refinement iteration 1 -> 2
[INFO] Saved refinement-0002.md
...
```

## Step 6: Monitor Progress

Open another terminal and watch your documents being created:

```bash
# Windows
dir generation\research-*\*.md

# Linux/Mac
ls generation/research-*/*.md
```

## Step 7: Stop When Ready

Press **Ctrl+C** to stop the refinement loop. Your documents are automatically saved!

## View Results

Navigate to your research directory:

```
generation/
  └── research-20250121-143022/
      ├── refinement-0001.md  ← Initial research
      ├── refinement-0002.md  ← First refinement
      ├── refinement-0003.md  ← Second refinement
      └── refinement-000N.md  ← Latest version
```

Open the latest refinement in your favorite markdown viewer or text editor.

## Troubleshooting

### "Connection refused" error

**Problem**: Can't connect to LMStudio

**Solution**:
1. Make sure LMStudio is running
2. Check the server is started (green indicator)
3. Verify port 1234 is open

### "Model not found" error

**Problem**: Model name doesn't match

**Solution**:
1. Check the exact model name in LMStudio
2. Update `config.yaml` with the correct name
3. Model names are case-sensitive!

### Slow performance

**Problem**: Taking too long to generate

**Solution**:
1. Use a smaller model (7B instead of 13B)
2. Reduce `num_workers` to 3 in config
3. Increase `refinement_delay` to 30 seconds
4. Enable GPU acceleration in LMStudio

### Agent errors

**Problem**: Agent fails with errors

**Solution**:
```bash
# Check Agno installation
pip install --upgrade agno

# Verify all dependencies
pip install -r requirements.txt --upgrade
```

## Next Steps

1. **Read [README.md](README.md)** for detailed documentation
2. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** to understand the system
3. **Experiment** with different topics
4. **Customize** the configuration
5. **Extend** with your own features

## Tips for Better Results

1. **Be specific** with your research topic
   - ❌ "AI"
   - ✅ "The impact of large language models on code generation"

2. **Use descriptive prompts**
   - ❌ "Tell me about space"
   - ✅ "Explain the latest discoveries about exoplanets and their potential for harboring life"

3. **Let it refine** for at least 5-10 iterations to see improvements

4. **Review intermediate versions** to see how the document evolves

## Example Topics

Try these to test the system:

```bash
# Technology
python research_orchestrator.py "The evolution of transformer architectures in NLP"

# Science
python research_orchestrator.py "CRISPR gene editing: current applications and ethical considerations"

# Business
python research_orchestrator.py "The impact of remote work on organizational culture and productivity"

# History
python research_orchestrator.py "The role of cryptography in World War II"

# Philosophy
python research_orchestrator.py "The philosophical implications of artificial consciousness"
```

## Getting Help

- Check [README.md](README.md) for detailed docs
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Open an issue on GitHub
- Check Agno documentation: https://docs.agno.com

---

**Happy researching!** 🚀
