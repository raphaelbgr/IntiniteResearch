"""Document refinement engine."""
from typing import Optional, Dict, Any, List, Tuple
import asyncio
from pathlib import Path
from storage.file_manager import FileManager
from storage.vector_store import VectorStore
from storage.source_kb import SourceKnowledgeBase
from agents.research_agent import ResearchAgent
from utils.context_manager import ContextManager
from utils.logger import get_logger

logger = get_logger()


class RefinementEngine:
    """Manages iterative document refinement."""

    def __init__(
        self,
        research_id: str,
        research_agent: ResearchAgent,
        file_manager: FileManager,
        vector_store: VectorStore,
        source_kb: SourceKnowledgeBase,
        refinement_delay: int = 10,
        input_files_content: str = "",
        enable_evaluation: bool = True,
        evaluation_frequency: int = 10
    ):
        """Initialize refinement engine.

        Args:
            research_id: Unique research identifier
            research_agent: Main research agent
            file_manager: File system manager
            vector_store: Vector database
            source_kb: Source knowledge base for URLs/sources
            refinement_delay: Seconds between refinements
            input_files_content: Not used (kept for compatibility)
            enable_evaluation: Enable evaluation loop (default: True)
            evaluation_frequency: Run evaluation every N iterations (default: 10)
        """
        self.research_id = research_id
        self.agent = research_agent
        self.file_manager = file_manager
        self.vector_store = vector_store
        self.source_kb = source_kb
        self.refinement_delay = refinement_delay
        self.enable_evaluation = enable_evaluation
        self.evaluation_frequency = evaluation_frequency
        self.context_manager = ContextManager()
        self.running = False

        logger.info(f"Initialized RefinementEngine for {research_id}")
        if enable_evaluation:
            logger.info(f"Evaluation reports every {evaluation_frequency} iterations")

    async def refine_once(
        self,
        version: int,
        base_topic: str
    ) -> Tuple[int, List[str]]:
        """Execute a single refinement iteration with context optimization.

        Args:
            version: Current version number
            base_topic: Original research topic

        Returns:
            Tuple of (new_version, search_terms_used)
        """
        logger.info(f"Starting refinement iteration {version} -> {version+1}")

        try:
            # Load last 2 refinements for context
            previous_refinements = await self.context_manager.load_last_refinements(
                self.file_manager,
                self.research_id,
                n=2
            )

            if not previous_refinements:
                logger.error(f"Could not load previous refinements")
                return version, []

            # Extract search terms from last iteration
            last_search_terms = []
            if previous_refinements:
                last_search_terms = previous_refinements[-1].get('search_terms', [])

            # Generate new search term variations
            new_search_terms = self.context_manager.generate_search_variations(
                base_topic=base_topic,
                previous_searches=last_search_terms,
                iteration=version + 1
            )

            from utils.beautiful_logger import BeautifulLogger
            blog = BeautifulLogger()
            blog.info(f"Generated [cyan]{len(new_search_terms)}[/cyan] search variations")

            # Identify research gaps
            gaps = self.context_manager.extract_research_gaps(previous_refinements)

            # Build context prompt with last 2 refinements
            # NOTE: Input files are NOT included in regular refinements
            # They're only used in iteration 1 and evaluation loops

            refinement_prompt = self.context_manager.build_context_prompt(
                base_prompt=self._build_refinement_instructions(
                    new_search_terms,
                    gaps
                ),
                previous_refinements=previous_refinements,
                input_files_content=""  # Never include in regular refinements
            )

            # Get context from vector store (minimal for weak models)
            vector_context = self._get_context_for_refinement(
                previous_refinements[-1]['content'],
                limit=3  # Reduced for weak models
            )

            # Refine document
            refined_content = await self.agent.refine(
                previous_content=refinement_prompt,
                context=vector_context
            )

            # Get the ACTUAL search terms used by AI from the active search provider(s)
            from tools import get_aggregated_search_data
            search_data = get_aggregated_search_data()

            # Use actual search terms if available, otherwise use suggested
            actual_search_terms = search_data['queries'] if search_data['queries'] else new_search_terms
            search_performance = search_data['performance']
            sources = search_data['sources']

            new_version = version + 1

            # Save sources to Knowledge Base (not in refinement file)
            sources_added = 0
            if sources:
                sources_added = self.source_kb.add_sources(
                    sources=sources,
                    iteration=new_version,
                    search_term=actual_search_terms[0] if actual_search_terms else None
                )

            # Save search performance to KB for learning
            if search_performance:
                self.source_kb.add_search_performance(search_performance, new_version)

            # Get KB summary for metadata
            kb_summary = self.source_kb.get_kb_summary()
            total_sources = self.source_kb.get_sources_count()

            # Format with metadata (search terms, performance, KB reference)
            formatted_content = self.context_manager.format_refinement_with_metadata(
                content=refined_content,
                search_terms=actual_search_terms,
                version=new_version,
                research_id=self.research_id,
                sources_count=total_sources,
                search_performance=search_performance,
                kb_summary=kb_summary
            )

            # Save new version
            await self.file_manager.save_refinement(
                self.research_id,
                new_version,
                formatted_content
            )

            # Add to vector store
            self._add_to_vector_store(new_version, formatted_content)

            # Update agent's knowledge base (only new content)
            self.agent.add_knowledge(
                formatted_content,
                metadata={'version': new_version}
            )

            # Display refinement iteration info
            from utils.beautiful_logger import BeautifulLogger
            blog = BeautifulLogger()
            blog.refinement_iteration(
                current_version=version,
                new_version=new_version,
                search_terms=new_search_terms,
                gaps=gaps,
                char_count=len(formatted_content)
            )

            # Display KB stats
            print(f"📚 Knowledge Base: {sources_added} new sources added | {total_sources} total in KB")

            logger.info(f"Refinement {new_version} completed")

            return new_version, new_search_terms

        except Exception as e:
            logger.error(f"Refinement failed: {e}", exc_info=True)
            return version, []

    def _build_refinement_instructions(
        self,
        search_terms: List[str],
        gaps: List[str]
    ) -> str:
        """Build refinement instructions.

        Args:
            search_terms: Suggested search terms
            gaps: Identified research gaps

        Returns:
            Refinement instructions
        """
        instructions = [
            "Refine and improve the research document based on previous iterations.\n\n",
            "**Suggested Search Terms for This Iteration:**\n"
        ]

        for term in search_terms:
            instructions.append(f"- {term}\n")

        instructions.append("\n")

        if gaps:
            instructions.append("**Identified Gaps to Address:**\n")
            for gap in gaps:
                instructions.append(f"- {gap}\n")
            instructions.append("\n")

        instructions.append(
            "**Your Task:**\n"
            "1. Use parallel searches with the suggested terms above\n"
            "2. Address identified gaps and weak sections\n"
            "3. Add depth, examples, and recent developments\n"
            "4. Improve clarity and organization\n"
            "5. Maintain consistency with previous iterations\n"
            "6. Do not remove important information\n\n"
        )

        return "".join(instructions)

    def _get_context_for_refinement(
        self,
        content: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get relevant context from vector store.

        Args:
            content: Document content to find context for
            limit: Maximum number of context items

        Returns:
            List of relevant context chunks
        """
        # Extract key phrases from content for search
        # Simple approach: use first 500 chars as query
        query = content[:500]

        try:
            context = self.vector_store.search_similar(
                query=query,
                limit=limit
            )
            logger.debug(f"Retrieved {len(context)} context items")
            return context
        except Exception as e:
            logger.warning(f"Context retrieval failed: {e}")
            return []

    def _add_to_vector_store(self, version: int, content: str):
        """Add document to vector store as chunks.

        Args:
            version: Version number
            content: Document content
        """
        try:
            # Simple chunking strategy: split by paragraphs
            chunks = self._chunk_document(content)

            # Add to vector store (without embeddings for now)
            # In production, generate embeddings using LMStudio or sentence-transformers
            self.vector_store.add_document_chunks(
                version=version,
                chunks=chunks,
                embeddings=None,  # TODO: Generate embeddings
                metadata={
                    'research_id': self.research_id,
                    'version': version,
                    'total_chunks': len(chunks)
                }
            )

            logger.debug(f"Added {len(chunks)} chunks to vector store")

        except Exception as e:
            logger.warning(f"Failed to add to vector store: {e}")

    def _chunk_document(
        self,
        content: str,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[str]:
        """Split document into chunks.

        Args:
            content: Document content
            chunk_size: Target size of each chunk (characters)
            overlap: Overlap between chunks (characters)

        Returns:
            List of text chunks
        """
        # Simple paragraph-based chunking
        paragraphs = content.split('\n\n')

        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > chunk_size and current_chunk:
                # Save current chunk
                chunks.append('\n\n'.join(current_chunk))

                # Start new chunk with overlap (keep last paragraph)
                if overlap > 0 and current_chunk:
                    current_chunk = [current_chunk[-1]]
                    current_size = len(current_chunk[-1])
                else:
                    current_chunk = []
                    current_size = 0

            current_chunk.append(para)
            current_size += para_size

        # Add final chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    async def refine_infinite(
        self,
        base_topic: str,
        starting_version: int = 1,
        evaluator = None
    ):
        """Run infinite refinement loop with iterative learning and evaluation.

        Args:
            base_topic: Original research topic
            starting_version: Version to start refinement from
            evaluator: Optional ResearchEvaluator for progress reports
        """
        logger.info("Starting infinite refinement loop (optimized for weak models)")
        logger.info(f"Strategy: Last 2 refinements + KB/RAG only")
        logger.info(f"Refinement delay: {self.refinement_delay} seconds")
        logger.info("Input files: Used in iteration 1 and evaluation loops only")
        if self.enable_evaluation and evaluator:
            logger.info(f"Evaluation reports every {self.evaluation_frequency} iterations")
        logger.info("Press Ctrl+C to stop")

        self.running = True
        current_version = starting_version
        iteration_count = 0
        evaluation_count = 0

        try:
            while self.running:
                iteration_count += 1

                # Check if we should run evaluation (every Nth iteration)
                run_evaluation = (
                    self.enable_evaluation and
                    evaluator and
                    iteration_count > 0 and
                    iteration_count % self.evaluation_frequency == 0
                )

                if run_evaluation:
                    # Run evaluation loop
                    evaluation_count += 1
                    await evaluator.run_evaluation_iteration(
                        current_version=current_version,
                        iteration_number=evaluation_count
                    )

                # Execute refinement with base topic for search variation
                new_version, search_terms = await self.refine_once(
                    current_version,
                    base_topic
                )

                # Check if refinement succeeded
                if new_version == current_version:
                    logger.warning("Refinement did not produce new version")
                    # Wait before retrying (interruptible)
                    await self._interruptible_sleep(self.refinement_delay)
                    continue

                # Update version
                current_version = new_version

                logger.info(
                    f"Iteration {iteration_count}: Refinement {current_version} complete "
                    f"with {len(search_terms)} search terms. "
                    f"Waiting {self.refinement_delay}s..."
                )

                # Wait before next refinement (interruptible)
                await self._interruptible_sleep(self.refinement_delay)

        except asyncio.CancelledError:
            logger.info("Refinement loop cancelled")
            self.running = False

        except Exception as e:
            logger.error(f"Refinement loop error: {e}", exc_info=True)
            self.running = False

        finally:
            logger.info(f"Refinement loop stopped at version {current_version}")
            logger.info(f"Total iterations: {iteration_count}")
            if self.enable_evaluation:
                logger.info(f"Evaluation reports generated: {evaluation_count}")

    async def _interruptible_sleep(self, seconds: int):
        """Sleep that can be interrupted by stop() signal.

        Args:
            seconds: Total seconds to sleep
        """
        # Sleep in 0.5 second chunks to allow quick interruption
        elapsed = 0
        while elapsed < seconds and self.running:
            await asyncio.sleep(0.5)
            elapsed += 0.5

    def stop(self):
        """Stop refinement loop."""
        logger.info("Stopping refinement loop...")
        self.running = False
