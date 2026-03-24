'''
Agentic Research: Operator supervising Infinite Research
'''

import threading
import queue
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

from agents.research_agent import ResearchAgent
from refinement.refiner import RefinementEngine
from storage.file_manager import FileManager
from storage.vector_store import VectorStore
from storage.source_kb import SourceKnowledgeBase
from utils.logger import get_logger

logger = get_logger()


class OperatorAgent:
    def __init__(self, lmstudio_config, session_dir):
        session_dir.mkdir(parents=True, exist_ok=True)  # Create dir first
        db_path = session_dir / "operator.db"
        self.storage = SqliteDb(db_url=f"sqlite:///{db_path}", session_table="operator")
        model = OpenAIChat(
            id=lmstudio_config.get("model", "local-model"),
            api_key=lmstudio_config.get("api_key", "lm-studio"),
            base_url=lmstudio_config.get("base_url", "http://localhost:1234/v1"),
            temperature=0.7, max_tokens=4096
        )
        self.agent = Agent(name="Operator", model=model, db=self.storage,
            instructions="""You are a Research Operator that STRICTLY maintains focus on the ORIGINAL OBJECTIVE.

CRITICAL RULES:
1. NEVER drift to unrelated topics (e.g., if objective is "marketplace plugins", don't search "crypto")
2. ALL search terms MUST directly serve the ORIGINAL OBJECTIVE
3. Evolution means DEEPER coverage of the SAME objective, NOT exploring tangents
4. Detect if current refinement has drifted off-topic - if so, REALIGN immediately

Response format:
**ALIGNED:** Yes/No - does refinement cover ORIGINAL objective?
**DRIFT CHECK:** [Are we still on the original topic? If not, REALIGN]
**Missing:** [gaps in covering the ORIGINAL objective]
**Evolved Terms:** "term1", "term2", "term3" (ALL must serve original objective)
**Evolution:** [how terms deepened focus on original objective]

NEVER suggest search terms unrelated to the original objective.""", markdown=True)

    def analyze(self, objective, refinement, iteration, user_msgs, previous_terms=None):
        feedback = ""
        if user_msgs:
            feedback = chr(10) + chr(10) + "═══ USER FEEDBACK ═══" + chr(10) + chr(10).join([f"→ {m}" for m in user_msgs])
        prev_terms_info = ""
        if previous_terms:
            prev_terms_info = f"{chr(10)}PREVIOUS TERMS: {', '.join([f'"{t}"' for t in previous_terms[:5]])}"
        
        prompt = f"""╔═══════════════════════════════════════════════════════════════╗
║              🎯 OPERATOR ANALYSIS TASK                        ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL: YOU MUST STAY STRICTLY ALIGNED TO THIS ORIGINAL PROMPT ⚠️

[ORIGINAL PROMPT] ← THIS IS YOUR ONLY FOCUS
{objective}

[CURRENT STATUS]
- Iteration: {iteration}
- Refinement preview: {refinement[:1500]}...{prev_terms_info}{feedback}

YOUR TASK:
1. DRIFT CHECK: Is the refinement still about the ORIGINAL PROMPT? (Not crypto, not unrelated topics)
2. If drifted: REALIGN search terms back to original objective
3. What specific gaps exist in covering the ORIGINAL PROMPT?
4. Suggest 3-4 search terms that DIRECTLY serve the ORIGINAL objective

REQUIRED FORMAT:
**ALIGNED:** Yes/No
**DRIFT CHECK:** [On topic? If not, explain drift and how to realign]
**Missing:** [gaps vs ORIGINAL prompt]
**Evolved Terms:** "term1", "term2", "term3" (MUST relate to original objective)
**Evolution:** [how terms stay anchored to original objective]

EXAMPLE - Staying Aligned:
Original: "Find marketplace plugin gaps for easy projects with existing clients"
✓ GOOD Terms: "Excel plugin marketplace opportunities", "Shopify app gaps 2025"
✗ BAD Terms: "crypto trading bots", "blockchain tools" (UNRELATED - don't drift!)

If you detect the refinement has drifted (e.g., talking about crypto when objective 
is plugins), immediately REALIGN with terms that serve the ORIGINAL objective."""
        
        response = self.agent.run(prompt)
        return response.content if hasattr(response, "content") else str(response)


class AgenticResearchSession:
    def __init__(self, research_id, research_dir, lmstudio_config, storage_config):
        self.research_id = research_id
        self.research_dir = research_dir
        self.lmstudio_config = lmstudio_config
        self.user_queue = queue.Queue()
        self.running = True
        self.max_iterations = 10
        
        # Initialize components properly
        self.file_manager = FileManager(base_dir=str(research_dir.parent))
        self.vector_store = VectorStore(research_id=research_id, base_dir=research_dir, db_type="sqlite")
        self.source_kb = SourceKnowledgeBase(research_id=research_id, base_dir=research_dir)
        
        self.operator = OperatorAgent(lmstudio_config, research_dir / "operator")
        self.research_agent = ResearchAgent(
            research_id=research_id,
            research_dir=research_dir,
            lmstudio_config=lmstudio_config,
            storage_config=storage_config
        )
        
        self.refiner = RefinementEngine(
            research_id=research_id,
            research_agent=self.research_agent,
            file_manager=self.file_manager,
            vector_store=self.vector_store,
            source_kb=self.source_kb,
            refinement_delay=5
        )
        self.previous_search_terms = []
        self.aligned_since_iteration = None  # Track when alignment achieved
        logger.info(f"AgenticResearchSession initialized: {research_id}")

    def start_input(self):
        def listen():
            print(chr(10) + "💬 Type guidance anytime - will be processed in NEXT iteration" + chr(10))
            while self.running:
                try:
                    msg = input("> ")
                    if msg.strip():
                        if msg.strip().lower() == "quit":
                            self.running = False
                            self.user_queue.put("__QUIT__")
                        else:
                            self.user_queue.put(msg.strip())
                            queue_size = self.user_queue.qsize()
                            msg_word = "message" if queue_size == 1 else "messages"
                            print(f"✓ Queued ({queue_size} {msg_word} pending)" + chr(10) + "> ", end="", flush=True)
                except: break
        threading.Thread(target=listen, daemon=True).start()

    def get_msgs(self):
        msgs = []
        while not self.user_queue.empty():
            try:
                m = self.user_queue.get_nowait()
                if m == "__QUIT__": self.running = False
                else: msgs.append(m)
            except queue.Empty: break
        return msgs

    async def run(self, topic):
        print(chr(10) + "=" * 70)
        print("  🎯 AGENTIC RESEARCH - Operator Supervised")
        print("=" * 70)
        print(f"{chr(10)}Objective: {topic}")
        print(chr(10) + "💡 How it works:")
        print("   • Operator analyzes each refinement for gaps")
        print("   • You can type guidance anytime (non-blocking)")
        print("   • Your messages are queued and processed in NEXT iteration")
        print("   • Type 'quit' to stop when satisfied")
        print("=" * 70)
        self.start_input()
        
        # Create initial refinement (v1) via research agent
        print(chr(10) + "🔍 [BOOTSTRAP] Creating initial research document...")
        initial_doc = await self.research_agent.research(f"Conduct comprehensive research on: {topic}")
        
        # Save as v1
        await self.file_manager.save_refinement(self.research_id, version=1, content=initial_doc)
        print("📄 [REFINEMENT v1] Initial document created")
        print("━" * 70)
        
        iteration = 0
        while iteration < self.max_iterations and self.running:
            iteration += 1
            print(chr(10) + "━" * 70)
            print(f"  🎯 Iteration {iteration}/{self.max_iterations}")
            print("━" * 70)
            
            user_msgs = self.get_msgs()
            
            print(chr(10) + "🔍 [RESEARCH] Conducting research...")
            new_ver, terms = await self.refiner.refine_once(version=iteration - 1, base_topic=topic)
            
            # Check if version incremented (0 means bootstrap failed, use iteration)
            if new_ver == 0:
                new_ver = iteration
            
            print(f"📄 [REFINEMENT v{new_ver}] Generated")
            
            ref_path = self.research_dir / f"refinement-{new_ver:04d}.md"
            if ref_path.exists():
                with open(ref_path, "r", encoding="utf-8") as f:
                    ref_content = f.read()
                
                if iteration < self.max_iterations and self.running:
                    if user_msgs:
                        print(chr(10) + f"💬 Processing {len(user_msgs)} user message(s):")
                        for m in user_msgs:
                            print(f"   → {m}")
                    # Display operator analysis in yellow box
                    print(chr(10) + "┌" + "─" * 68 + "┐")
                    print("│" + " " * 20 + "🎯 OPERATOR ANALYSIS" + " " * 27 + "│")
                    print("└" + "─" * 68 + "┘")
                    
                    analysis = self.operator.analyze(topic, ref_content, iteration, user_msgs, self.previous_search_terms)
                    
                    # Display analysis in yellow box with original prompt at top
                    print("[93m┏" + "━" * 68 + "┓[0m")
                    
                    # Show original prompt first
                    print(f"[93m┃[0m [1m[Original Prompt][0m" + " " * 49 + "[93m┃[0m")
                    original_lines = topic.split(chr(10)) if chr(10) in topic else [topic]
                    for orig_line in original_lines:
                        if len(orig_line) > 64:
                            # Wrap long lines
                            for j in range(0, len(orig_line), 64):
                                chunk = orig_line[j:j+64]
                                padding = " " * (66 - len(chunk))
                                print(f"[93m┃[0m [96m{chunk}[0m{padding} [93m┃[0m")
                        else:
                            padding = " " * (66 - len(orig_line))
                            print(f"[93m┃[0m [96m{orig_line}[0m{padding} [93m┃[0m")
                    
                    print("[93m┃" + " " * 68 + "┃[0m")
                    
                    # Show analysis
                    for line in analysis.split(chr(10)):
                        display_line = line[:66]
                        padding = " " * (66 - len(display_line))
                        print(f"[93m┃[0m {display_line}{padding} [93m┃[0m")
                    print("[93m┗" + "━" * 68 + "┛[0m" + chr(10))
                    
                    # Check for drift
                    import re
                    if "DRIFT CHECK:" in analysis and "Off topic" in analysis:
                        print("[91m╔" + "═" * 68 + "╗[0m")
                        print("[91m║[0m [1m⚠️  TOPIC DRIFT DETECTED - REALIGNING[0m" + " " * 31 + "[91m║[0m")
                        print("[91m║[0m   Operator detected drift from original objective         [91m║[0m")
                        print("[91m║[0m   Next iteration will realign to original prompt         [91m║[0m")
                        print("[91m╚" + "═" * 68 + "╝[0m" + chr(10))
                    
                    # Check for alignment
                    if "**ALIGNED:** Yes" in analysis or "ALIGNED: Yes" in analysis:
                        if self.aligned_since_iteration is None:
                            self.aligned_since_iteration = iteration
                        # Show alignment warning
                        print("[92m╔" + "═" * 68 + "╗[0m")
                        print(f"[92m║[0m [1m⚠️  ALIGNMENT ACHIEVED (since iteration {self.aligned_since_iteration})[0m" + " " * (66 - 42 - len(str(self.aligned_since_iteration))) + "[92m║[0m")
                        print("[92m║[0m   Refinement comprehensively covers the original objective.  [92m║[0m")
                        print("[92m║[0m   Research continues to deepen coverage.                    [92m║[0m")
                        print("[92m║[0m   You can type 'quit' to stop if satisfied.                [92m║[0m")
                        print("[92m╚" + "═" * 68 + "╝[0m" + chr(10))
                    
                    # Extract and store evolved terms
                    evolved_terms = re.findall(r'"([^"]+)"', analysis)
                    if evolved_terms:
                        self.previous_search_terms = evolved_terms
                        print("[93m📈 EVOLVED SEARCH TERMS:[0m")
                        for i, term in enumerate(evolved_terms[:4], 1):
                            print(f"[93m   {i}.[0m {term}")
                        print()
                    
                    time.sleep(1)
            else:
                print(f"   (Refinement file not found: {ref_path})")
        
        self.running = False
        print(chr(10) + "=" * 70)
        print("  ✓ AGENTIC RESEARCH COMPLETE")
        print("=" * 70)
        print(f"{chr(10)}Final: {ref_path}")
        return ref_path
