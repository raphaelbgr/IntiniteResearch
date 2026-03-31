# BMAD Auto Mode - Quick Reference

## ✅ Problem FIXED!

The orchestrator was calling `run_interactive()` instead of `run_auto_mode()`.
This has been corrected in `research_orchestrator.py`.

## How to Run (NO PROMPTS!)

### Option 1: Use the main orchestrator
```bash
python research_orchestrator.py --bmad "Your research objective here"
```

### Option 2: Use the dedicated runner
```bash
python run_bmad_auto.py
```

### Option 3: Programmatic
```python
from pathlib import Path
from agents.bmad_orchestrator import BMadResearchSession

session = BMadResearchSession(
    research_id="test-001",
    research_dir=Path("./generation/test"),
    lmstudio_config={
        'model': 'local-model',
        'base_url': 'http://localhost:1234/v1',
        'api_key': 'lm-studio',
        'temperature': 0.7,
        'max_tokens': 4096
    }
)

# 100% AUTOMATED - NO PROMPTS!
import asyncio
asyncio.run(session.run_auto_mode(goal="Your goal here"))
```

## What You'll See

Instead of the old:
```
You: _
```

You'll now see:
```
╭─ 🤖 BMAD Auto Mode ────────────────╮
│ Starting FULLY AUTOMATED Mode      │
│ Goal: Your research goal           │
│                                    │
│ The Operator (AI) will make all    │
│ decisions automatically.           │
│ This is 100% autonomous!           │
╰────────────────────────────────────╯

🤖 Operator is thinking...

╭─ 🤖 Operator (Auto-User) ──────────╮
│ I would like to explore...         │
╰────────────────────────────────────╯

📡 Consulting the team...

╭─ 👥 Team Response ─────────────────╮
│ Based on your request...           │
╰────────────────────────────────────╯
```

## Changes Made

1. **`research_orchestrator.py`** (Lines 660 & 859):
   - Changed: `await bmad_session.run_interactive()`
   - To: `await bmad_session.run_auto_mode(goal=research_topic)`

2. **`agents/bmad_orchestrator.py`**:
   - Added `BMadOperator` class (AI that acts as user)
   - Added `run_auto_mode()` to both session types
   - Operator makes ALL decisions automatically

## Safety Features

- **Max 20 Operator turns** before auto-conclude
- **Max 30 total iterations** before force-conclude
- **Context truncation** to prevent memory issues
- **Ctrl+C** to interrupt anytime
- **Error recovery** with graceful shutdown

## NO MORE PROMPTS! 🎉

The system is now **100% autonomous**. The Operator AI will:
✅ Read all messages
✅ Make all decisions
✅ Ask follow-up questions
✅ Decide when to conclude
✅ Never ask YOU for input

Sit back and watch the beautiful CLI output!
