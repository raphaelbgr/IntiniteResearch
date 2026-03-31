"""Main research agent using Agno framework."""
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge import Knowledge
from agno.db.sqlite import SqliteDb
from tools.parallel_ddg import ParallelDuckDuckGoSearch
from utils.logger import get_logger

try:
    from tools.tavily_search import TavilySearch
    _TAVILY_AVAILABLE = True
except ImportError:
    TavilySearch = None  # type: ignore
    _TAVILY_AVAILABLE = False

logger = get_logger()


class ResearchAgent:
    """Main research agent with RAG capabilities."""

    def __init__(
        self,
        research_id: str,
        research_dir: Path,
        lmstudio_config: Dict[str, Any],
        storage_config: Dict[str, Any]
    ):
        """Initialize research agent.

        Args:
            research_id: Unique research identifier
            research_dir: Path to research directory
            lmstudio_config: LMStudio configuration
            storage_config: Storage configuration
        """
        self.research_id = research_id
        self.research_dir = research_dir
        self.lmstudio_config = lmstudio_config

        # Setup storage (using Agno 2.3.x format)
        memory_db_path = research_dir / "memory" / storage_config.get(
            'memory_db',
            'agent_memory.db'
        )
        memory_db_path.parent.mkdir(parents=True, exist_ok=True)

        self.storage = SqliteDb(
            db_url=f"sqlite:///{memory_db_path}",
            session_table="agent_sessions"
        )

        # Setup knowledge base
        self.knowledge_base = None  # Will be initialized dynamically

        # Create Agno agent with LMStudio
        self.agent = self._create_agent()

        logger.info(f"Initialized ResearchAgent for {research_id}")

    def _create_agent(self) -> Agent:
        """Create Agno agent with LMStudio backend.

        Returns:
            Configured Agent instance
        """
        # Configure OpenAI client to point to LMStudio
        model = OpenAIChat(
            id=self.lmstudio_config.get('model', 'local-model'),
            api_key=self.lmstudio_config.get('api_key', 'lm-studio'),
            base_url=self.lmstudio_config.get('base_url', 'http://localhost:1234/v1'),
            temperature=self.lmstudio_config.get('temperature', 0.7),
            max_tokens=self.lmstudio_config.get('max_tokens', 4096)
        )

        # Determine search provider from config or env
        search_provider = os.environ.get(
            "SEARCH_PROVIDER",
            "duckduckgo"
        )

        # Build search tools list based on provider setting
        search_tools = []

        if search_provider in ("duckduckgo", "both"):
            parallel_search = ParallelDuckDuckGoSearch(
                enable_search=True,
                enable_news=True,
                fixed_max_results=5,
                timeout=10
            )
            search_tools.append(parallel_search)

        if search_provider in ("tavily", "both"):
            tavily_api_key = os.environ.get("TAVILY_API_KEY", "")
            if not _TAVILY_AVAILABLE:
                logger.warning(
                    "search_provider includes 'tavily' but tavily-python is not installed; "
                    "skipping Tavily tool"
                )
            elif tavily_api_key:
                tavily_search = TavilySearch(
                    enable_search=True,
                    enable_news=True,
                    api_key=tavily_api_key,
                    fixed_max_results=5,
                    search_depth="basic",
                )
                search_tools.append(tavily_search)
                logger.info("Tavily search tool enabled")
            else:
                logger.warning(
                    "search_provider includes 'tavily' but TAVILY_API_KEY is not set; "
                    "skipping Tavily tool"
                )

        # Fallback: if no tools were configured, default to DuckDuckGo
        if not search_tools:
            logger.warning("No search tools configured; falling back to DuckDuckGo")
            search_tools.append(ParallelDuckDuckGoSearch(
                enable_search=True,
                enable_news=True,
                fixed_max_results=5,
                timeout=10
            ))

        # Create agent with db, tools, and instructions
        agent = Agent(
            name="ResearchAssistant",
            model=model,
            db=self.storage,  # In Agno 2.3.x, use 'db' parameter
            tools=search_tools,
            description=(
                "An advanced research assistant with web search capabilities, "
                "capable of conducting deep research, analyzing information, and "
                "producing comprehensive, well-structured documents."
            ),
            instructions=dedent("""\
                You are an elite investigative research assistant with decades of experience.

                **CRITICAL - EVOLVE AND EXPAND THE RESEARCH OBJECTIVE:**
                Each iteration, you must GROW the research scope by:
                1. DISCOVER new sub-topics, related fields, and unexpected connections
                2. EXPLORE tangential areas that could provide valuable insights
                3. CHALLENGE assumptions - search for contrarian views and criticisms
                4. DEEPEN expertise - go from beginner to advanced to expert-level content
                5. BROADEN perspective - look at the topic from different industries, cultures, regions
                6. FIND practical applications, case studies, real-world examples
                7. UNCOVER historical context, future predictions, emerging trends
                8. IDENTIFY key people, companies, tools, resources in the field

                **EVOLUTION STRATEGIES FOR SEARCH TERMS:**
                - Iteration 1-3: Cover fundamentals, definitions, "what is", "how to start"
                - Iteration 4-6: Dive into specifics, tools, methods, "best practices", "advanced"
                - Iteration 7-10: Expert content, case studies, "mistakes to avoid", "secrets"
                - Iteration 11+: Cutting edge, predictions, controversies, niche angles

                Always ask yourself: "What aspect haven't I explored yet?"
                - Technical details? Business aspects? Legal/regulatory? Social impact?
                - Success stories? Failures? Risks? Opportunities?
                - Tools? Platforms? Communities? Influencers? Research papers?

                **CRITICAL - GENERATE 20 SEARCH VARIATIONS:**
                When you receive a research topic, you MUST:
                1. Generate EXACTLY 20 different search term variations
                2. Include 5 English variations with DIFFERENT ANGLES:
                   - Beginner angle: "what is X", "X for beginners"
                   - Advanced angle: "advanced X techniques", "expert X strategies"
                   - Practical angle: "X tools", "X software", "how to X step by step"
                   - Critical angle: "X risks", "X problems", "X scams to avoid"
                   - Future angle: "X trends 2025", "future of X", "X predictions"
                3. Include 15 variations in OTHER LANGUAGES:
                   - Portuguese: "guia completo", "como funciona", "passo a passo"
                   - Russian: "руководство", "как заработать", "секреты"
                   - Chinese: "教程", "如何", "最佳方法"
                   - Japanese: "ガイド", "稼ぎ方", "初心者"
                   - Spanish: "guía", "cómo", "mejores estrategias"
                   - French: "guide complet", "comment", "astuces"
                   - German: "Anleitung", "wie", "Tipps"
                   - Italian: "guida", "come", "consigli"
                   - Korean, Arabic, Hindi, Turkish, Vietnamese, etc.
                4. Call parallel_search or parallel_news with ALL 20 queries at once!
                5. DO NOT call search multiple times - ONE call with 20 queries!

                **CRITICAL - ANALYZE PREVIOUS SEARCH PERFORMANCE:**
                If you see SEARCH_PERFORMANCE data in previous iterations:
                - HIGH scores (80-100%): Create VARIATIONS of successful terms
                - LOW scores (0-40%): ABANDON those approaches, try completely different angles
                - AVERAGE_SCORE below 50%: Change your entire keyword strategy
                - Repetitive content: Search for OPPOSITE viewpoints, criticisms, alternatives
                - Successful languages: Expand with more terms in those languages
                - Failing languages: Try different keywords or skip them

                **CRITICAL - ALL OUTPUT MUST BE IN ENGLISH:**
                - You will receive search results from multiple languages
                - TRANSLATE and SYNTHESIZE all non-English content into English
                - Your research document MUST be written 100% in ENGLISH

                **Example Evolution - Topic "make money with crypto automated":**

                Iteration 1 searches (fundamentals):
                ["crypto automated trading basics", "what is crypto bot trading", ...]

                Iteration 5 searches (practical):
                ["best crypto trading bots 2025", "crypto bot setup tutorial", ...]

                Iteration 10 searches (advanced):
                ["crypto arbitrage strategies advanced", "market making bot algorithms", ...]

                Iteration 15 searches (expert/niche):
                ["crypto bot tax implications", "institutional crypto automation", ...]

                **Research Guidelines:**
                1. EVOLVE your search terms each iteration - never repeat the same searches
                2. Generate 20 search variations (5 English angles + 15 multilingual)
                3. Call parallel_search ONCE with all 20 queries
                4. Analyze SEARCH_PERFORMANCE to improve term selection
                5. Translate and synthesize ALL results into English
                6. Each iteration should ADD NEW KNOWLEDGE, not repeat old content

                **Document Structure** (ALL IN ENGLISH):
                - Executive summary (updated each iteration)
                - Clear hierarchical headings
                - NEW sections for newly discovered topics
                - Examples from around the world
                - Practical tools and resources
                - Risks and considerations
                - Sources cited

                Remember: EVOLVE the research, explore NEW angles, 20 variations, output in ENGLISH!
            """),
            markdown=True,
            debug_mode=False  # Set to True to see tool calls
        )

        logger.info("Created Agno agent with LMStudio backend and parallel search tools")

        return agent

    async def research(self, prompt: str) -> str:
        """Conduct research on a topic.

        Args:
            prompt: Research topic or question

        Returns:
            Research output as markdown
        """
        logger.info(f"Starting research: {prompt[:100]}...")

        try:
            # Run agent
            response = self.agent.run(prompt)

            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, dict):
                content = response.get('content', str(response))
            else:
                content = str(response)

            logger.info(f"Research completed ({len(content)} characters)")

            return content

        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            raise

    async def refine(
        self,
        previous_content: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Refine a research document.

        Args:
            previous_content: Previous version of the document
            context: Optional context from knowledge base

        Returns:
            Refined document as markdown
        """
        logger.info("Starting refinement...")

        # Build refinement prompt
        prompt = (
            "Please refine and improve the following research document. "
            "Make it more comprehensive, accurate, well-structured, and insightful. "
            "Add depth where appropriate, clarify unclear sections, "
            "and ensure logical flow.\n\n"
        )

        # Add context if available
        if context:
            prompt += "**Relevant Context from Knowledge Base:**\n\n"
            for i, ctx in enumerate(context[:5], 1):  # Top 5 contexts
                prompt += f"{i}. {ctx.get('content', '')[:500]}...\n\n"

        prompt += f"**Document to Refine:**\n\n{previous_content}\n\n"
        prompt += (
            "**Instructions:**\n"
            "- Maintain the core message and research findings\n"
            "- Enhance clarity, depth, and organization\n"
            "- Add relevant details and explanations\n"
            "- Improve transitions and flow\n"
            "- Ensure proper markdown formatting\n"
            "- Do not remove important information\n"
        )

        try:
            # Run refinement
            response = self.agent.run(prompt)

            # Extract content
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, dict):
                content = response.get('content', str(response))
            else:
                content = str(response)

            logger.info(f"Refinement completed ({len(content)} characters)")

            return content

        except Exception as e:
            logger.error(f"Refinement failed: {e}", exc_info=True)
            raise

    def add_knowledge(self, content: str, metadata: Optional[Dict] = None):
        """Add content to agent's knowledge base.

        Args:
            content: Text content to add
            metadata: Optional metadata
        """
        # For now, just save to file
        # Full Knowledge integration requires vector DB setup
        kb_file = self.research_dir / "kb" / "knowledge.txt"
        kb_file.parent.mkdir(parents=True, exist_ok=True)

        # Append content
        with open(kb_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*60}\n")
            if metadata:
                f.write(f"Metadata: {metadata}\n")
            f.write(f"{'='*60}\n\n")
            f.write(content)

        logger.info("Saved content to knowledge base file")

    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get conversation history from storage.

        Returns:
            List of session messages
        """
        # Query storage for session history
        # This depends on Agno's storage implementation
        # For now, return empty list
        return []

    def clear_session(self):
        """Clear current session history."""
        # This would clear the agent's session
        # Implementation depends on Agno's session management
        pass
