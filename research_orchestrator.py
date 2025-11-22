#!/usr/bin/env python3
"""
Infinite Research Refinement System
Main orchestrator script

Usage:
    python research_orchestrator.py "Your research topic here"
"""

import sys
import os
import asyncio
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional

# Fix Windows console encoding for Unicode characters (Russian, Chinese, Japanese, etc.)
if sys.platform == 'win32':
    # Set Windows console to UTF-8 code page
    os.system('chcp 65001 > nul 2>&1')
    # Set environment variable for Python IO encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Reconfigure stdout/stderr to use UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from utils.config_loader import (
    load_config,
    get_lmstudio_config,
    get_research_config,
    get_vector_db_config,
    get_storage_config
)
from utils.logger import setup_logger, get_logger
from utils.file_selector import FileSelector
from utils.context_manager import ContextManager
from utils.research_selector import ResearchSelector
from storage.file_manager import FileManager
from storage.vector_store import VectorStore
from storage.source_kb import SourceKnowledgeBase
from agents.research_agent import ResearchAgent
from refinement.refiner import RefinementEngine
from refinement.evaluator import ResearchEvaluator


class ResearchOrchestrator:
    """Main orchestrator for infinite research refinement system."""

    def __init__(
        self,
        config_path: str = "config.yaml",
        enable_evaluation: Optional[bool] = None,
        evaluation_frequency: Optional[int] = None
    ):
        """Initialize orchestrator.

        Args:
            config_path: Path to configuration file
            enable_evaluation: Enable evaluation reports (default: from config or True)
            evaluation_frequency: Evaluation every N iterations (default: from config or 10)
        """
        # Load configuration
        self.config = load_config(config_path)

        # Setup beautiful logging
        log_config = self.config.get('logging', {})
        self.logger = setup_logger(
            level=log_config.get('level', 'INFO'),
            log_file=log_config.get('file', 'research.log'),
            console=log_config.get('console', True)
        )

        # Display beautiful banner
        self.logger.banner([
            "Infinite Research Refinement System",
            "Powered by Agno + LMStudio",
            "Parallel DuckDuckGo Search (1-10 queries)",
            "Optimized for Weak Models"
        ])

        # Extract configurations
        self.lmstudio_config = get_lmstudio_config(self.config)
        self.research_config = get_research_config(self.config)
        self.vector_db_config = get_vector_db_config(self.config)
        self.storage_config = get_storage_config(self.config)

        # Evaluation configuration (CLI args override config)
        self.enable_evaluation = (
            enable_evaluation if enable_evaluation is not None
            else self.research_config.get('enable_evaluation', True)
        )
        self.evaluation_frequency = (
            evaluation_frequency if evaluation_frequency is not None
            else self.research_config.get('evaluation_frequency', 10)
        )

        # Initialize components
        self.file_manager = FileManager(
            base_dir=self.research_config.get('output_dir', './generation')
        )
        self.file_selector = FileSelector(input_dir="./input")
        self.context_manager = ContextManager()
        self.research_selector = ResearchSelector(self.file_manager)

        # State
        self.research_id: str = ""
        self.research_dir: Path = Path()
        self.research_agent: ResearchAgent = None
        self.vector_store: VectorStore = None
        self.source_kb: SourceKnowledgeBase = None
        self.refinement_engine: RefinementEngine = None
        self.evaluator: ResearchEvaluator = None
        self.running = True
        self.base_topic: str = ""
        self.input_files_content: str = ""
        self.auto_select_files: Optional[str] = None

        # Display model info
        self.logger.model_info(
            model_name=self.lmstudio_config.get('model', 'local-model'),
            base_url=self.lmstudio_config.get('base_url', 'http://localhost:1234/v1')
        )

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        self._interrupt_count = 0

        def signal_handler(signum, frame):
            self._interrupt_count += 1

            if self._interrupt_count == 1:
                self.logger.info("\n\n⚠️  Ctrl+C detected - stopping gracefully...")
                self.logger.info("Press Ctrl+C again to force quit immediately")
                self.running = False
                if self.refinement_engine:
                    self.refinement_engine.stop()
            else:
                # Second Ctrl+C - force exit
                self.logger.info("\n\n🛑 Force quitting...")
                sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        # SIGTERM only works on Unix, skip on Windows
        if sys.platform != 'win32':
            signal.signal(signal.SIGTERM, signal_handler)

    async def initialize_research(self, research_topic: str) -> str:
        """Initialize a new research session with file selection.

        Args:
            research_topic: Research topic or prompt

        Returns:
            Research ID
        """
        self.logger.header("Initialization", style="bold cyan")
        self.logger.info(f"Topic: [bold]{research_topic[:100]}...[/bold]")
        self.base_topic = research_topic

        # Interactive file selection (or auto-select if specified)
        selected_files = self.file_selector.select_files(auto_select=self.auto_select_files)

        # Generate research ID
        self.research_id = self.file_manager.create_research_id()
        self.logger.success(f"Research ID: {self.research_id}")

        # Create directory structure
        self.research_dir = self.file_manager.create_research_directory(
            self.research_id
        )

        # Copy selected files to research session
        if selected_files:
            copied_files = self.file_selector.copy_files_to_session(
                selected_files,
                self.research_dir
            )

            # Read input files for context
            self.input_files_content = self.file_selector.read_input_files(copied_files)

            self.logger.success(f"Copied {len(copied_files)} input file(s) to session")
            for f in copied_files:
                self.logger.list_item(f.name)
        else:
            self.input_files_content = ""
            self.logger.info("[dim]No input files selected[/dim]")

        # Save metadata
        metadata = {
            'research_id': self.research_id,
            'topic': research_topic,
            'started_at': datetime.now().isoformat(),
            'config': {
                'parallel_search': 'enabled',
                'refinement_delay': self.research_config.get('refinement_delay', 10)
            }
        }
        await self.file_manager.save_metadata(self.research_id, metadata)

        # Initialize vector store
        self.vector_store = VectorStore(
            research_id=self.research_id,
            base_dir=self.research_dir,
            db_type=self.vector_db_config.get('type', 'sqlite')
        )

        # Initialize source knowledge base
        self.source_kb = SourceKnowledgeBase(
            research_id=self.research_id,
            base_dir=self.research_dir
        )

        # Initialize research agent (with parallel search tools)
        self.research_agent = ResearchAgent(
            research_id=self.research_id,
            research_dir=self.research_dir,
            lmstudio_config=self.lmstudio_config,
            storage_config=self.storage_config
        )

        # Initialize evaluator if enabled
        if self.enable_evaluation:
            self.evaluator = ResearchEvaluator(
                research_id=self.research_id,
                research_agent=self.research_agent,
                file_manager=self.file_manager,
                research_dir=self.research_dir,
                base_topic=self.base_topic,
                input_files_content=self.input_files_content
            )

        # Initialize refinement engine with evaluation config
        self.refinement_engine = RefinementEngine(
            research_id=self.research_id,
            research_agent=self.research_agent,
            file_manager=self.file_manager,
            vector_store=self.vector_store,
            source_kb=self.source_kb,
            refinement_delay=self.research_config.get('refinement_delay', 10),
            input_files_content="",  # Not used in regular refinements
            enable_evaluation=self.enable_evaluation,
            evaluation_frequency=self.evaluation_frequency
        )

        self.logger.info("Research session initialized with parallel search agent")
        if self.input_files_content:
            self.logger.section(
                "Input File Strategy",
                "• Used in: Iteration 1 (initial research)\n"
                "• Used in: Evaluation loops (every 10th iteration)\n"
                "• NOT used in: Regular refinements (iterations 2-10, 12-20, etc.)",
                style="yellow"
            )
        if self.enable_evaluation:
            self.logger.info(f"Evaluation reports enabled (every {self.evaluation_frequency} iterations)")

        return self.research_id

    async def continue_research(self, session_info: dict) -> int:
        """Continue an existing research session.

        Args:
            session_info: Dict with research_id, topic, latest_version, etc.

        Returns:
            Latest version number to continue from
        """
        self.logger.header("Continuing Research Session", style="bold green")

        self.research_id = session_info['research_id']
        self.base_topic = session_info['topic']
        latest_version = session_info['latest_version']

        self.logger.info(f"Research ID: [bold]{self.research_id}[/bold]")
        self.logger.info(f"Topic: [bold]{self.base_topic[:80]}...[/bold]")
        self.logger.info(f"Continuing from version: [cyan]{latest_version}[/cyan]")

        # Get research directory
        self.research_dir = self.file_manager.get_research_directory(self.research_id)

        # Load existing metadata
        metadata = await self.file_manager.load_metadata(self.research_id)
        if metadata:
            self.logger.info(f"Started: {metadata.get('started_at', 'Unknown')}")
            if metadata.get('total_sources'):
                self.logger.info(f"Sources in KB: {metadata.get('total_sources')}")

        # Initialize vector store (reconnect to existing)
        self.vector_store = VectorStore(
            research_id=self.research_id,
            base_dir=self.research_dir,
            db_type=self.vector_db_config.get('type', 'sqlite')
        )

        # Initialize source knowledge base (reconnect to existing)
        self.source_kb = SourceKnowledgeBase(
            research_id=self.research_id,
            base_dir=self.research_dir
        )

        # Show existing KB stats
        kb_sources = self.source_kb.get_sources_count()
        kb_stats = self.source_kb.get_search_term_stats()
        print(f"\n📚 Existing Knowledge Base:")
        print(f"   • Sources: {kb_sources}")
        print(f"   • Searches performed: {kb_stats['total_searches']}")
        print(f"   • Average score: {kb_stats['avg_score']:.1f}%")

        # Initialize research agent
        self.research_agent = ResearchAgent(
            research_id=self.research_id,
            research_dir=self.research_dir,
            lmstudio_config=self.lmstudio_config,
            storage_config=self.storage_config
        )

        # Initialize evaluator if enabled
        if self.enable_evaluation:
            self.evaluator = ResearchEvaluator(
                research_id=self.research_id,
                research_agent=self.research_agent,
                file_manager=self.file_manager,
                research_dir=self.research_dir,
                base_topic=self.base_topic,
                input_files_content=""  # Not loading input files for continuation
            )

        # Initialize refinement engine
        self.refinement_engine = RefinementEngine(
            research_id=self.research_id,
            research_agent=self.research_agent,
            file_manager=self.file_manager,
            vector_store=self.vector_store,
            source_kb=self.source_kb,
            refinement_delay=self.research_config.get('refinement_delay', 10),
            input_files_content="",
            enable_evaluation=self.enable_evaluation,
            evaluation_frequency=self.evaluation_frequency
        )

        # Load last refinement into agent's knowledge
        last_content = await self.file_manager.load_refinement(self.research_id, latest_version)
        if last_content:
            self.research_agent.add_knowledge(
                last_content,
                metadata={'version': latest_version, 'type': 'continued'}
            )
            self.logger.success(f"Loaded refinement-{latest_version:04d}.md into agent memory")

        self.logger.success("Research session restored successfully!")

        return latest_version

    async def conduct_initial_research(self, research_topic: str) -> str:
        """Conduct initial research with parallel DuckDuckGo searches.

        Args:
            research_topic: Research topic or prompt

        Returns:
            Initial research document
        """
        self.logger.phase_start(1, "Initial Research with Parallel Search")
        self.logger.info("Agent will execute parallel DuckDuckGo searches (up to 20 queries)")
        self.logger.separator()

        # Build research prompt with input files if available
        research_prompt_parts = []

        if self.input_files_content:
            research_prompt_parts.append(self.input_files_content)
            research_prompt_parts.append("\n---\n\n")

        research_prompt_parts.append(
            f"Conduct comprehensive research on the following topic. "
            f"Use parallel web searches to gather information from multiple angles:\n\n"
            f"**Topic:** {research_topic}\n\n"
            f"Break down the topic into 5-7 key aspects and search for each aspect. "
            f"Synthesize the findings into a well-structured research document."
        )

        research_prompt = "".join(research_prompt_parts)

        # Execute research with parallel search capabilities
        research_doc = await self.research_agent.research(research_prompt)

        # Get the ACTUAL search terms used by AI from the parallel_search tool
        from tools.parallel_ddg import ParallelDuckDuckGoSearch
        search_data = ParallelDuckDuckGoSearch.get_last_search_data()

        # Use actual search terms from the AI's searches
        actual_search_terms = search_data['queries'] if search_data['queries'] else ['initial research']
        search_performance = search_data['performance']
        sources = search_data['sources']

        # Save sources to Knowledge Base (not in refinement file)
        sources_added = 0
        if sources:
            sources_added = self.source_kb.add_sources(
                sources=sources,
                iteration=1,
                search_term=actual_search_terms[0] if actual_search_terms else None
            )

        # Save search performance to KB for learning
        if search_performance:
            self.source_kb.add_search_performance(search_performance, iteration=1)

        # Get KB summary for metadata
        kb_summary = self.source_kb.get_kb_summary()
        total_sources = self.source_kb.get_sources_count()

        # Format with metadata (actual search terms, performance, KB reference)
        formatted_doc = self.context_manager.format_refinement_with_metadata(
            content=research_doc,
            search_terms=actual_search_terms,
            version=1,
            research_id=self.research_id,
            sources_count=total_sources,
            search_performance=search_performance,
            kb_summary=kb_summary
        )

        # Save as version 1
        await self.file_manager.save_refinement(
            self.research_id,
            version=1,
            content=formatted_doc
        )

        # Add to vector store
        self.refinement_engine._add_to_vector_store(1, formatted_doc)

        # Add to agent's knowledge base
        self.research_agent.add_knowledge(
            formatted_doc,
            metadata={'version': 1, 'type': 'initial_research'}
        )

        self.logger.success("Initial research completed: refinement-0001.md")
        self.logger.info(f"Search terms used: {len(actual_search_terms)}")
        if actual_search_terms:
            for term in actual_search_terms[:5]:
                self.logger.list_item(term[:60])
            if len(actual_search_terms) > 5:
                self.logger.info(f"  ... and {len(actual_search_terms) - 5} more")

        # Display KB stats
        print(f"\n📚 Knowledge Base initialized:")
        print(f"   • {sources_added} sources added to KB")
        print(f"   • {total_sources} total sources in KB")
        if sources:
            # Show top domains found
            top_domains = self.source_kb.get_top_domains(5)
            if top_domains:
                print(f"   • Top domains: {', '.join(d['domain'] for d in top_domains[:3])}")

        return formatted_doc

    async def run_refinement_loop(self, starting_version: int = 1):
        """Run infinite refinement loop with iterative learning.

        Args:
            starting_version: Version to continue from (1 for new, or latest for continue)
        """
        if starting_version == 1:
            self.logger.phase_start(2, "Infinite Refinement Loop")
        else:
            self.logger.phase_start(2, f"Continuing Refinement Loop (from v{starting_version})")

        self.logger.section(
            "Strategy",
            "• Context: Last 2 refinements + KB/RAG\n"
            "• Learning: Search terms evolve each iteration\n"
            "• Stop: Press Ctrl+C when satisfied",
            style="cyan"
        )

        # Start refinement from specified version with base topic and evaluator
        await self.refinement_engine.refine_infinite(
            base_topic=self.base_topic,
            starting_version=starting_version,
            evaluator=self.evaluator
        )

    async def run(self, research_topic: str):
        """Main execution flow for NEW research.

        Args:
            research_topic: Research topic or prompt
        """
        try:
            # Setup signal handlers
            self._setup_signal_handlers()

            # Initialize research session
            await self.initialize_research(research_topic)

            # Conduct initial parallel research
            await self.conduct_initial_research(research_topic)

            # Run infinite refinement loop (starting from version 1)
            await self.run_refinement_loop(starting_version=1)

        except KeyboardInterrupt:
            self.logger.info("\n\nResearch interrupted by user")

        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)

        finally:
            await self.cleanup()

    async def run_continue(self, session_info: dict):
        """Main execution flow for CONTINUING existing research.

        Args:
            session_info: Dict with research session details
        """
        try:
            # Setup signal handlers
            self._setup_signal_handlers()

            # Continue existing research session
            latest_version = await self.continue_research(session_info)

            # Run infinite refinement loop (continuing from last version)
            await self.run_refinement_loop(starting_version=latest_version)

        except KeyboardInterrupt:
            self.logger.info("\n\nResearch interrupted by user")

        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)

        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup resources."""
        self.logger.header("Cleanup", style="cyan")

        # Get KB stats before closing (for metadata)
        kb_total_sources = 0
        kb_stats = {'total_searches': 0, 'avg_score': 0}
        if self.source_kb:
            kb_total_sources = self.source_kb.get_sources_count()
            kb_stats = self.source_kb.get_search_term_stats()
            # Display final KB stats
            print(f"\n📚 Final Knowledge Base Stats:")
            print(f"   • Total unique sources: {kb_total_sources}")
            print(f"   • Total searches performed: {kb_stats['total_searches']}")
            print(f"   • Average search score: {kb_stats['avg_score']:.1f}%")

        # Close vector store
        if self.vector_store:
            self.vector_store.close()
            self.logger.success("Vector store closed")

        # Close source knowledge base
        if self.source_kb:
            self.source_kb.close()
            self.logger.success("Source knowledge base closed")

        # Update metadata with end time
        if self.research_id:
            metadata = await self.file_manager.load_metadata(self.research_id)
            if metadata:
                metadata['ended_at'] = datetime.now().isoformat()
                final_version = self.file_manager.get_latest_version(self.research_id)
                metadata['final_version'] = final_version
                metadata['total_sources'] = kb_total_sources
                metadata['total_searches'] = kb_stats['total_searches']
                metadata['avg_search_score'] = kb_stats['avg_score']
                await self.file_manager.save_metadata(self.research_id, metadata)

                # Display final summary
                self.logger.final_summary(
                    research_id=self.research_id,
                    total_versions=final_version,
                    total_sources=kb_total_sources,
                    research_dir=str(self.research_dir)
                )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Infinite Research Refinement System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python research_orchestrator.py                    # Interactive menu
  python research_orchestrator.py "AI in healthcare" # New research
  python research_orchestrator.py --continue         # Continue latest
  python research_orchestrator.py --continue research-20250122-143022

Note: Input files are automatically used in iteration 1 and evaluation loops.
For more info, see README.md and ITERATION_FLOW.md
        """
    )

    parser.add_argument(
        "topic",
        type=str,
        nargs='?',  # Make topic optional
        default=None,
        help="Research topic or question (optional - shows menu if not provided)"
    )

    parser.add_argument(
        "--continue",
        dest="continue_research",
        type=str,
        nargs='?',
        const='latest',
        default=None,
        help="Continue existing research. Use 'latest' or specify research ID"
    )

    parser.add_argument(
        "--enable-eval",
        dest="enable_evaluation",
        action="store_true",
        default=None,
        help="Enable evaluation reports (default: enabled)"
    )

    parser.add_argument(
        "--no-eval",
        dest="enable_evaluation",
        action="store_false",
        help="Disable evaluation reports"
    )

    parser.add_argument(
        "--eval-freq",
        dest="evaluation_frequency",
        type=int,
        default=None,
        help="Run evaluation every N iterations (default: 10)"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)"
    )

    parser.add_argument(
        "--no-input",
        action="store_true",
        help="Skip input file selection (use no files)"
    )

    parser.add_argument(
        "--input-files",
        type=str,
        default=None,
        help="Comma-separated list of input file indices (e.g., '1' for all, '2,3' for specific)"
    )

    args = parser.parse_args()

    # Handle input file selection
    auto_select = None
    if args.no_input:
        auto_select = "0"
    elif args.input_files:
        auto_select = args.input_files

    # Create orchestrator with CLI args
    orchestrator = ResearchOrchestrator(
        config_path=args.config,
        enable_evaluation=args.enable_evaluation,
        evaluation_frequency=args.evaluation_frequency
    )
    orchestrator.auto_select_files = auto_select

    try:
        # Determine action: continue, new with topic, or interactive menu
        if args.continue_research:
            # Auto-continue specified or latest research
            result = orchestrator.research_selector.select_or_new(
                auto_continue=args.continue_research
            )
            if result is None:
                print("No research to continue.")
                sys.exit(0)

            action, session_info = result
            if action == 'continue' and session_info:
                asyncio.run(orchestrator.run_continue(session_info))
            else:
                print("No continuable research found.")
                sys.exit(1)

        elif args.topic:
            # New research with provided topic
            asyncio.run(orchestrator.run(args.topic))

        else:
            # Interactive menu - no topic provided
            result = orchestrator.research_selector.display_menu()

            if result is None:
                print("\nExiting...")
                sys.exit(0)

            action, session_info = result

            if action == 'new':
                # Get topic from user
                print()
                topic = input("Enter research topic: ").strip()
                if not topic:
                    print("No topic provided. Exiting.")
                    sys.exit(0)
                asyncio.run(orchestrator.run(topic))

            elif action == 'continue' and session_info:
                asyncio.run(orchestrator.run_continue(session_info))

    except KeyboardInterrupt:
        print("\n\n✅ Research session ended.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Ensure clean exit
        print("Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
