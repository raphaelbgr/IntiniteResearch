"""Parallel research worker pool."""
from typing import List, Dict, Any
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from utils.logger import get_logger

logger = get_logger()


class WorkerPool:
    """Manages parallel research workers."""

    def __init__(
        self,
        num_workers: int,
        lmstudio_config: Dict[str, Any],
        research_dir: Path
    ):
        """Initialize worker pool.

        Args:
            num_workers: Number of parallel workers
            lmstudio_config: LMStudio configuration
            research_dir: Path to research directory
        """
        self.num_workers = num_workers
        self.lmstudio_config = lmstudio_config
        self.research_dir = research_dir
        self.workers: List[Agent] = []

        self._create_workers()

        logger.info(f"Initialized worker pool with {num_workers} workers")

    def _create_workers(self):
        """Create worker agents."""
        for i in range(self.num_workers):
            # Configure OpenAI client for LMStudio
            model = OpenAIChat(
                id=self.lmstudio_config.get('model', 'local-model'),
                api_key=self.lmstudio_config.get('api_key', 'lm-studio'),
                base_url=self.lmstudio_config.get('base_url', 'http://localhost:1234/v1'),
                temperature=0.7,
                max_tokens=2048  # Smaller for workers
            )

            # Create worker agent
            worker = Agent(
                name=f"ResearchWorker-{i+1}",
                model=model,
                description=f"Research worker #{i+1} specializing in focused topic investigation",
                instructions=[
                    "You are a focused research worker.",
                    "Investigate your assigned subtopic thoroughly.",
                    "Provide detailed findings with key points.",
                    "Be concise but comprehensive.",
                    "Focus on factual, verifiable information."
                ],
                markdown=True,
                show_tool_calls=False
            )

            self.workers.append(worker)

        logger.debug(f"Created {len(self.workers)} worker agents")

    def decompose_topic(self, main_topic: str) -> List[str]:
        """Decompose main topic into subtopics for parallel research.

        Args:
            main_topic: Main research topic

        Returns:
            List of subtopics
        """
        # Simple decomposition strategy
        # In production, you could use an LLM to intelligently decompose
        subtopics = [
            f"Overview and introduction to: {main_topic}",
            f"Historical background and context of: {main_topic}",
            f"Current state and recent developments in: {main_topic}",
            f"Key challenges and limitations of: {main_topic}",
            f"Future trends and implications of: {main_topic}"
        ]

        # Adjust number of subtopics to match workers
        while len(subtopics) < self.num_workers:
            subtopics.append(f"Additional perspectives on: {main_topic}")

        return subtopics[:self.num_workers]

    async def research_parallel(self, main_topic: str) -> List[Dict[str, Any]]:
        """Execute parallel research on subtopics.

        Args:
            main_topic: Main research topic

        Returns:
            List of research results from each worker
        """
        logger.info(f"Starting parallel research on: {main_topic}")

        # Decompose topic
        subtopics = self.decompose_topic(main_topic)

        logger.info(f"Decomposed into {len(subtopics)} subtopics")

        # Create research tasks
        tasks = []
        for i, (worker, subtopic) in enumerate(zip(self.workers, subtopics)):
            task = self._worker_research(worker, subtopic, i)
            tasks.append(task)

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Worker {i+1} failed: {result}")
            else:
                valid_results.append(result)

        logger.info(
            f"Parallel research completed: "
            f"{len(valid_results)}/{len(results)} workers succeeded"
        )

        return valid_results

    async def _worker_research(
        self,
        worker: Agent,
        subtopic: str,
        worker_id: int
    ) -> Dict[str, Any]:
        """Execute research for a single worker.

        Args:
            worker: Worker agent
            subtopic: Subtopic to research
            worker_id: Worker identifier

        Returns:
            Research result dictionary
        """
        logger.debug(f"Worker {worker_id+1} researching: {subtopic[:50]}...")

        try:
            # Run worker on subtopic
            response = worker.run(
                f"Research the following topic in detail:\n\n{subtopic}\n\n"
                f"Provide a comprehensive analysis with key findings."
            )

            # Extract content
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, dict):
                content = response.get('content', str(response))
            else:
                content = str(response)

            result = {
                'worker_id': worker_id,
                'subtopic': subtopic,
                'content': content,
                'success': True
            }

            logger.debug(
                f"Worker {worker_id+1} completed "
                f"({len(content)} characters)"
            )

            return result

        except Exception as e:
            logger.error(f"Worker {worker_id+1} error: {e}", exc_info=True)
            return {
                'worker_id': worker_id,
                'subtopic': subtopic,
                'content': "",
                'success': False,
                'error': str(e)
            }

    def aggregate_results(self, results: List[Dict[str, Any]]) -> str:
        """Aggregate worker results into a single document.

        Args:
            results: List of worker research results

        Returns:
            Aggregated document as markdown
        """
        logger.info("Aggregating worker results...")

        # Build aggregated document
        doc_parts = [
            "# Research Document\n",
            "\n*Compiled from parallel research workers*\n\n",
            "---\n\n"
        ]

        for result in results:
            if result.get('success', False):
                doc_parts.append(f"## {result['subtopic']}\n\n")
                doc_parts.append(result['content'])
                doc_parts.append("\n\n---\n\n")

        aggregated = "".join(doc_parts)

        logger.info(
            f"Aggregated {len(results)} results "
            f"into {len(aggregated)} character document"
        )

        return aggregated
