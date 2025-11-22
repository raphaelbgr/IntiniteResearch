"""Main research agent using Agno framework."""
from typing import Dict, Any, Optional, List
from pathlib import Path
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge import Knowledge
from agno.db.sqlite import SqliteDb
from tools.parallel_ddg import ParallelDuckDuckGoSearch
from utils.logger import get_logger

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

        # Initialize parallel search tool
        parallel_search = ParallelDuckDuckGoSearch(
            enable_search=True,
            enable_news=True,
            fixed_max_results=5,
            timeout=10
        )

        # Create agent with db, tools, and instructions
        agent = Agent(
            name="ResearchAssistant",
            model=model,
            db=self.storage,  # In Agno 2.3.x, use 'db' parameter
            tools=[parallel_search],
            description=(
                "An advanced research assistant with web search capabilities, "
                "capable of conducting deep research, analyzing information, and "
                "producing comprehensive, well-structured documents."
            ),
            instructions=dedent("""\
                You are an elite investigative research assistant with decades of experience.

                **CRITICAL - GENERATE 20 SEARCH VARIATIONS:**
                When you receive a research topic, you MUST:
                1. Generate EXACTLY 20 different search term variations
                2. Include 5 English variations with different angles (basics, advanced, tools, etc.)
                3. Include 15 variations in OTHER LANGUAGES:
                   - Portuguese: "crypto guia completo", "como funciona"
                   - Russian: "криптовалюта руководство", "как заработать"
                   - Chinese: "加密货币 教程", "如何赚钱"
                   - Japanese: "仮想通貨 ガイド", "稼ぎ方"
                   - Spanish: "criptomonedas guía", "cómo ganar"
                   - French: "crypto guide complet", "comment gagner"
                   - German: "Krypto Anleitung", "wie verdienen"
                   - Italian: "cripto guida", "come guadagnare"
                   - Norwegian, Finnish, Polish, Dutch, Swedish, etc.
                4. Call parallel_search or parallel_news with ALL 20 queries at once!
                5. DO NOT call search multiple times - ONE call with 20 queries!

                **CRITICAL - ANALYZE PREVIOUS SEARCH PERFORMANCE:**
                If you see SEARCH_PERFORMANCE data in previous iterations:
                - Look at which terms got HIGH scores (80-100%) - create similar variations
                - Look at which terms got LOW scores (0-40%) - try completely different approaches
                - If AVERAGE_SCORE is below 50%, change your keyword strategy entirely
                - If content is getting repetitive, try NEW keyword combinations
                - Successful languages should be expanded, failing languages can be skipped

                **CRITICAL - ALL OUTPUT MUST BE IN ENGLISH:**
                - You will receive search results from multiple languages
                - TRANSLATE and SYNTHESIZE all non-English content into English
                - Your research document MUST be written 100% in ENGLISH

                **Example of what to do:**
                For topic "make money with crypto automated":
                Call parallel_search with these 20 queries:
                [
                  "crypto automated trading guide",
                  "passive income cryptocurrency 2025",
                  "crypto trading bots tutorial",
                  "automated crypto strategies",
                  "crypto passive income methods",
                  "criptomonedas ingresos pasivos guía",
                  "криптовалюта пассивный доход",
                  "加密货币 被动收入 教程",
                  "仮想通貨 自動売買 ガイド",
                  "crypto renda passiva como",
                  "cryptomonnaie revenu passif guide",
                  "Krypto passives Einkommen",
                  "cripto reddito passivo guida",
                  "kryptovaluta passiv inntekt",
                  "kryptovaluutta passiivinen tulo",
                  "kryptowaluta dochód pasywny",
                  "crypto passief inkomen gids",
                  "kryptovaluta passiv inkomst",
                  "crypto automated free tools",
                  "best crypto bots 2025"
                ]

                **Research Guidelines:**
                1. Generate 20 search variations (5 English + 15 multilingual)
                2. Call parallel_search ONCE with all 20 queries
                3. Analyze previous SEARCH_PERFORMANCE to improve term selection
                4. Translate and synthesize ALL results into English

                **Document Structure** (ALL IN ENGLISH):
                - Executive summary
                - Clear hierarchical headings
                - Examples from around the world
                - Sources cited

                Remember: 20 variations, analyze performance, improve terms, output in ENGLISH!
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
