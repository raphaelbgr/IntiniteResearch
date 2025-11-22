"""Evaluation loop for comparing research progress against objectives."""
from typing import Dict, Any, List, Optional
from pathlib import Path
from agents.research_agent import ResearchAgent
from storage.file_manager import FileManager
from utils.context_manager import ContextManager
from utils.logger import get_logger

logger = get_logger()


class ResearchEvaluator:
    """Evaluates research progress against user objectives."""

    def __init__(
        self,
        research_id: str,
        research_agent: ResearchAgent,
        file_manager: FileManager,
        research_dir: Path,
        base_topic: str,
        input_files_content: str = ""
    ):
        """Initialize research evaluator.

        Args:
            research_id: Unique research identifier
            research_agent: Main research agent
            file_manager: File system manager
            research_dir: Research directory path
            base_topic: Original research topic/prompt
            input_files_content: User-provided input files
        """
        self.research_id = research_id
        self.agent = research_agent
        self.file_manager = file_manager
        self.research_dir = research_dir
        self.base_topic = base_topic
        self.input_files_content = input_files_content
        self.context_manager = ContextManager()

        # Create report directory
        self.report_dir = research_dir / "report"
        self.report_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized ResearchEvaluator for {research_id}")

    async def evaluate_progress(self, current_version: int) -> str:
        """Evaluate research progress against objectives.

        Args:
            current_version: Current refinement version

        Returns:
            Evaluation report as markdown
        """
        logger.info(f"Evaluating research progress at version {current_version}")

        # Load latest refinement
        latest_content = await self.file_manager.load_refinement(
            self.research_id,
            current_version
        )

        if not latest_content:
            logger.error(f"Could not load version {current_version} for evaluation")
            return ""

        # Build evaluation prompt
        evaluation_prompt = self._build_evaluation_prompt(
            latest_content=latest_content,
            base_topic=self.base_topic,
            input_files_content=self.input_files_content
        )

        try:
            # Run evaluation
            report = await self.agent.research(evaluation_prompt)

            logger.info(f"Evaluation completed ({len(report)} characters)")

            return report

        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            return f"# Evaluation Failed\n\nError: {e}"

    def _build_evaluation_prompt(
        self,
        latest_content: str,
        base_topic: str,
        input_files_content: str
    ) -> str:
        """Build evaluation prompt.

        Args:
            latest_content: Latest refinement content
            base_topic: Original research topic
            input_files_content: User input files

        Returns:
            Evaluation prompt
        """
        # Remove metadata from latest content for clean comparison
        import re
        clean_content = re.sub(
            r'<!-- .+? -->',
            '',
            latest_content,
            flags=re.DOTALL
        ).strip()

        # Limit content size for weak models
        if len(clean_content) > 3000:
            clean_content = clean_content[:3000] + "\n\n*[Content truncated]*"

        prompt_parts = [
            "# Research Progress Evaluation\n\n",
            "You are evaluating the progress of an ongoing research project.\n\n",
            "## Original Objective\n\n",
            f"**Topic:** {base_topic}\n\n"
        ]

        # Add user input files if available
        if input_files_content:
            prompt_parts.append("## User's Reference Materials\n\n")
            prompt_parts.append(
                "*The user provided these materials to guide the research:*\n\n"
            )
            # Truncate input files for weak models
            truncated_input = input_files_content
            if len(truncated_input) > 2000:
                truncated_input = truncated_input[:2000] + "\n\n*[Input truncated]*"
            prompt_parts.append(truncated_input)
            prompt_parts.append("\n\n")

        # Add current research state
        prompt_parts.append("## Current Research Document\n\n")
        prompt_parts.append("*This is the latest version of the research:*\n\n")
        prompt_parts.append(clean_content)
        prompt_parts.append("\n\n")

        # Evaluation instructions
        prompt_parts.append("## Your Task: Evaluate Progress\n\n")
        prompt_parts.append("Please provide a comprehensive evaluation:\n\n")

        prompt_parts.append("### 1. **Objective Alignment** (1-10 scale)\n")
        prompt_parts.append(
            "How well does the current research address the original topic?\n"
            "Rate from 1 (not aligned) to 10 (perfectly aligned).\n\n"
        )

        prompt_parts.append("### 2. **Completeness** (1-10 scale)\n")
        prompt_parts.append(
            "How complete is the research? Are all key aspects covered?\n\n"
        )

        if input_files_content:
            prompt_parts.append("### 3. **Alignment with Reference Materials** (1-10 scale)\n")
            prompt_parts.append(
                "How well does the research incorporate or address the user's "
                "reference materials?\n\n"
            )

        prompt_parts.append("### 4. **Research Gaps**\n")
        prompt_parts.append(
            "List specific gaps, missing information, or areas that need more depth:\n"
            "- Gap 1\n"
            "- Gap 2\n"
            "- etc.\n\n"
        )

        prompt_parts.append("### 5. **Strengths**\n")
        prompt_parts.append("What are the strong points of the current research?\n\n")

        prompt_parts.append("### 6. **Recommendations**\n")
        prompt_parts.append(
            "Specific recommendations for future refinement iterations:\n"
            "- Recommendation 1\n"
            "- Recommendation 2\n"
            "- etc.\n\n"
        )

        prompt_parts.append("### 7. **Overall Progress** (percentage)\n")
        prompt_parts.append(
            "Estimate overall completion: X% toward fully addressing the objective.\n\n"
        )

        prompt_parts.append(
            "**Note:** Be honest and constructive. This evaluation helps guide "
            "future refinement iterations.\n"
        )

        return "".join(prompt_parts)

    async def save_report(
        self,
        version: int,
        iteration_number: int,
        report_content: str
    ) -> Path:
        """Save evaluation report.

        Args:
            version: Current refinement version
            iteration_number: Evaluation iteration number
            report_content: Report content

        Returns:
            Path to saved report
        """
        report_filename = f"report-{iteration_number:04d}.md"
        report_path = self.report_dir / report_filename

        # Add metadata
        from datetime import datetime

        metadata_parts = [
            f"<!-- REPORT_NUMBER: {iteration_number:04d} -->",
            f"<!-- EVALUATED_VERSION: {version:04d} -->",
            f"<!-- TIMESTAMP: {datetime.now().isoformat()} -->",
            "",
            "---",
            ""
        ]

        formatted_report = "\n".join(metadata_parts) + report_content

        # Save report
        import aiofiles
        async with aiofiles.open(report_path, 'w', encoding='utf-8') as f:
            await f.write(formatted_report)

        logger.info(f"Saved evaluation report: {report_filename}")

        return report_path

    async def run_evaluation_iteration(
        self,
        current_version: int,
        iteration_number: int
    ) -> Path:
        """Run a complete evaluation iteration.

        Args:
            current_version: Current refinement version
            iteration_number: Evaluation iteration number

        Returns:
            Path to saved report
        """
        from utils.beautiful_logger import BeautifulLogger
        blog = BeautifulLogger()

        blog.header("Evaluation Loop", style="bold magenta")
        blog.info(f"Evaluating refinement [cyan]{current_version:04d}[/cyan]")
        blog.info(f"Evaluation iteration: [magenta]{iteration_number}[/magenta]")
        blog.separator()

        # Run evaluation
        report = await self.evaluate_progress(current_version)

        # Save report
        report_path = await self.save_report(
            version=current_version,
            iteration_number=iteration_number,
            report_content=report
        )

        blog.success(f"Evaluation report saved: [cyan]{report_path.name}[/cyan]")
        blog.separator()

        return report_path
