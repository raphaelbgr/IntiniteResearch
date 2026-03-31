"""Research Compiler - Generates conclusions from accumulated research."""
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from storage.file_manager import FileManager
from storage.source_kb import SourceKnowledgeBase
from agents.research_agent import ResearchAgent
from utils.logger import get_logger

logger = get_logger()


class ResearchCompiler:
    """Compiles research refinements into a final conclusion document."""

    def __init__(
        self,
        research_id: str,
        research_dir: Path,
        file_manager: FileManager,
        source_kb: SourceKnowledgeBase,
        research_agent: ResearchAgent,
        base_topic: str
    ):
        """Initialize compiler.

        Args:
            research_id: Research session ID
            research_dir: Path to research directory
            file_manager: FileManager instance
            source_kb: Source knowledge base
            research_agent: Research agent for AI processing
            base_topic: Original research topic/objective
        """
        self.research_id = research_id
        self.research_dir = research_dir
        self.file_manager = file_manager
        self.source_kb = source_kb
        self.agent = research_agent
        self.base_topic = base_topic

        # Create conclusion directory
        self.conclusion_dir = research_dir / "conclusion"
        self.conclusion_dir.mkdir(exist_ok=True)

        # Accumulated state
        self.accumulated_points: List[str] = []
        self.processed_versions: List[int] = []
        self.objective_satisfaction: int = 0  # 0-100%

    async def compile_research(self) -> Optional[Path]:
        """Main compilation flow with user interaction.

        Returns:
            Path to final conclusion file, or None if cancelled
        """
        print("\n" + "=" * 70)
        print("  RESEARCH COMPILATION - Generate Conclusion")
        print("=" * 70)

        # Get all versions
        latest_version = self.file_manager.get_latest_version(self.research_id)
        if latest_version == 0:
            print("\nNo refinements found to compile.")
            return None

        print(f"\nResearch: {self.base_topic[:60]}...")
        print(f"Versions available: 1 to {latest_version}")
        print(f"Sources in KB: {self.source_kb.get_sources_count()}")

        # Show KB stats
        stats = self.source_kb.get_search_term_stats()
        print(f"Total searches: {stats['total_searches']}")
        print(f"Avg search score: {stats['avg_score']:.1f}%")

        print("\n" + "-" * 70)
        print("This will analyze all refinements and generate a comprehensive conclusion.")
        print("You'll be able to guide the process at each step.")
        print("-" * 70)

        # Ask how to proceed
        choice = self._ask_compilation_mode(latest_version)
        if choice is None:
            return None

        if choice == 'quick':
            # Quick compilation - process all at once
            return await self._quick_compile(latest_version)
        elif choice == 'guided':
            # Guided compilation - step by step with user input
            return await self._guided_compile(latest_version)
        elif choice == 'custom':
            # Custom range
            start, end = self._ask_version_range(latest_version)
            if start is None:
                return None
            return await self._guided_compile(end, start_version=start)

        return None

    def _ask_compilation_mode(self, latest_version: int) -> Optional[str]:
        """Ask user for compilation mode.

        Returns:
            'quick', 'guided', 'custom', or None to cancel
        """
        print("\nCompilation Options:")
        print(f"  [1] Quick - Compile all {latest_version} versions automatically")
        print(f"  [2] Guided - Step through each version with options")
        print(f"  [3] Custom - Select specific version range")
        print(f"  [0] Cancel")

        while True:
            try:
                choice = input("\nSelect mode: ").strip()
                if choice == '0':
                    return None
                elif choice == '1':
                    return 'quick'
                elif choice == '2':
                    return 'guided'
                elif choice == '3':
                    return 'custom'
                else:
                    print("Invalid choice. Enter 0-3")
            except KeyboardInterrupt:
                return None

    def _ask_version_range(self, latest_version: int) -> Tuple[Optional[int], Optional[int]]:
        """Ask user for version range.

        Returns:
            Tuple of (start_version, end_version) or (None, None)
        """
        print(f"\nAvailable versions: 1 to {latest_version}")
        try:
            start = input("Start version (default: 1): ").strip()
            start = int(start) if start else 1

            end = input(f"End version (default: {latest_version}): ").strip()
            end = int(end) if end else latest_version

            if start < 1 or end > latest_version or start > end:
                print("Invalid range.")
                return None, None

            return start, end
        except (ValueError, KeyboardInterrupt):
            return None, None

    async def _quick_compile(self, latest_version: int) -> Optional[Path]:
        """Quick compilation - process all versions automatically.

        Args:
            latest_version: Latest version number

        Returns:
            Path to conclusion file
        """
        print(f"\nQuick compiling {latest_version} versions...")

        # Process versions from latest to oldest (most refined first)
        all_key_points = []

        for version in range(latest_version, 0, -1):
            print(f"  Processing version {version}...", end=" ", flush=True)

            content = await self.file_manager.load_refinement(self.research_id, version)
            if not content:
                print("skip (not found)")
                continue

            # Extract key points using AI
            key_points = await self._extract_key_points(content, version)
            all_key_points.extend(key_points)
            self.processed_versions.append(version)

            print(f"found {len(key_points)} key points")

        # Deduplicate and prioritize points
        self.accumulated_points = self._deduplicate_points(all_key_points)

        print(f"\nTotal unique key points: {len(self.accumulated_points)}")

        # Check objective satisfaction
        self.objective_satisfaction = await self._check_objective_satisfaction()
        print(f"Objective satisfaction: {self.objective_satisfaction}%")

        # Generate final conclusion
        return await self._generate_conclusion()

    async def _guided_compile(
        self,
        latest_version: int,
        start_version: int = 1
    ) -> Optional[Path]:
        """Guided compilation - step through with user interaction.

        Args:
            latest_version: End version
            start_version: Start version

        Returns:
            Path to conclusion file
        """
        print(f"\nGuided compilation: versions {start_version} to {latest_version}")
        print("At each step, you can add notes or skip to next.\n")

        # Process versions from latest to oldest
        for version in range(latest_version, start_version - 1, -1):
            print(f"\n{'=' * 50}")
            print(f"VERSION {version}")
            print("=" * 50)

            content = await self.file_manager.load_refinement(self.research_id, version)
            if not content:
                print("Not found, skipping...")
                continue

            # Extract and show key points
            key_points = await self._extract_key_points(content, version)

            print(f"\nKey points extracted ({len(key_points)}):")
            for i, point in enumerate(key_points[:10], 1):
                print(f"  {i}. {point[:100]}...")

            if len(key_points) > 10:
                print(f"  ... and {len(key_points) - 10} more")

            # User options
            action = self._ask_version_action(version, key_points)

            if action == 'quit':
                print("\nStopping compilation...")
                break
            elif action == 'skip':
                print("Skipping this version...")
                continue
            elif action == 'accept':
                self.accumulated_points.extend(key_points)
                self.processed_versions.append(version)
                print(f"Added {len(key_points)} points. Total: {len(self.accumulated_points)}")
            elif action == 'select':
                selected = self._select_points(key_points)
                self.accumulated_points.extend(selected)
                self.processed_versions.append(version)
                print(f"Added {len(selected)} points. Total: {len(self.accumulated_points)}")
            elif action == 'note':
                note = input("Enter your note: ").strip()
                if note:
                    self.accumulated_points.append(f"[USER NOTE] {note}")
                self.accumulated_points.extend(key_points)
                self.processed_versions.append(version)

            # Show progress
            self._show_progress()

            # Ask to continue or finalize
            if version > start_version:
                cont = input("\nContinue to next version? [Y/n]: ").strip().lower()
                if cont == 'n':
                    break

        # Deduplicate
        self.accumulated_points = self._deduplicate_points(self.accumulated_points)

        # Check objective satisfaction
        print("\n" + "=" * 50)
        print("OBJECTIVE CHECK")
        print("=" * 50)
        self.objective_satisfaction = await self._check_objective_satisfaction()
        print(f"\nObjective satisfaction: {self.objective_satisfaction}%")
        print(f"Total key points: {len(self.accumulated_points)}")

        # Final options
        final_action = self._ask_final_action()

        if final_action == 'generate':
            return await self._generate_conclusion()
        elif final_action == 'add_more':
            # User can add more notes
            while True:
                note = input("\nAdd note (empty to finish): ").strip()
                if not note:
                    break
                self.accumulated_points.append(f"[USER NOTE] {note}")
            return await self._generate_conclusion()
        elif final_action == 'cancel':
            print("Compilation cancelled.")
            return None

        return None

    def _ask_version_action(self, version: int, key_points: List[str]) -> str:
        """Ask user what to do with this version's points.

        Returns:
            'accept', 'skip', 'select', 'note', or 'quit'
        """
        print("\nOptions:")
        print("  [1] Accept all points")
        print("  [2] Select specific points")
        print("  [3] Skip this version")
        print("  [4] Add a note + accept")
        print("  [0] Stop and generate conclusion")

        while True:
            try:
                choice = input("Choice: ").strip()
                if choice == '0':
                    return 'quit'
                elif choice == '1':
                    return 'accept'
                elif choice == '2':
                    return 'select'
                elif choice == '3':
                    return 'skip'
                elif choice == '4':
                    return 'note'
                else:
                    print("Invalid. Enter 0-4")
            except KeyboardInterrupt:
                return 'quit'

    def _select_points(self, key_points: List[str]) -> List[str]:
        """Let user select specific points.

        Returns:
            List of selected points
        """
        print("\nEnter point numbers to include (comma-separated, e.g., 1,3,5):")
        print("Or 'all' for all, 'none' for none")

        for i, point in enumerate(key_points, 1):
            print(f"  [{i}] {point[:80]}...")

        try:
            selection = input("\nSelection: ").strip().lower()

            if selection == 'all':
                return key_points
            elif selection == 'none':
                return []
            else:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                return [key_points[i] for i in indices if 0 <= i < len(key_points)]
        except (ValueError, KeyboardInterrupt):
            return []

    def _ask_final_action(self) -> str:
        """Ask user for final action.

        Returns:
            'generate', 'add_more', or 'cancel'
        """
        print("\nFinal Options:")
        print("  [1] Generate conclusion document")
        print("  [2] Add more notes first")
        print("  [0] Cancel")

        while True:
            try:
                choice = input("Choice: ").strip()
                if choice == '0':
                    return 'cancel'
                elif choice == '1':
                    return 'generate'
                elif choice == '2':
                    return 'add_more'
                else:
                    print("Invalid. Enter 0-2")
            except KeyboardInterrupt:
                return 'cancel'

    def _show_progress(self):
        """Show current compilation progress."""
        print(f"\n--- Progress: {len(self.processed_versions)} versions, "
              f"{len(self.accumulated_points)} points ---")

    async def _extract_key_points(self, content: str, version: int) -> List[str]:
        """Extract key points from a refinement using AI.

        Args:
            content: Refinement content
            version: Version number

        Returns:
            List of key points
        """
        # Truncate content if too long
        max_content = 4000
        if len(content) > max_content:
            content = content[:max_content] + "\n\n[Content truncated...]"

        prompt = f"""Analyze this research document and extract the KEY POINTS.

**RESEARCH DOCUMENT (Version {version}):**
{content}

**INSTRUCTIONS:**
Extract 5-15 key points that represent the most important findings, facts, insights, or conclusions.
Each point should be a single, clear statement.
Focus on:
- Main findings and conclusions
- Important facts and statistics
- Practical recommendations
- Key insights and discoveries

**OUTPUT FORMAT:**
Return ONLY a numbered list of key points, one per line:
1. First key point
2. Second key point
...

Do not include any other text, just the numbered list."""

        try:
            response = await self.agent.research(prompt)

            # Parse response into list
            points = []
            for line in response.split('\n'):
                line = line.strip()
                # Remove numbering
                if line and line[0].isdigit():
                    # Remove "1. " or "1) " prefix
                    if '. ' in line:
                        line = line.split('. ', 1)[1]
                    elif ') ' in line:
                        line = line.split(') ', 1)[1]
                    if line:
                        points.append(line)

            return points[:15]  # Cap at 15 points per version

        except Exception as e:
            logger.warning(f"Failed to extract points from version {version}: {e}")
            return []

    def _deduplicate_points(self, points: List[str]) -> List[str]:
        """Remove duplicate or very similar points.

        Args:
            points: List of all points

        Returns:
            Deduplicated list
        """
        if not points:
            return []

        unique = []
        seen_normalized = set()

        for point in points:
            # Normalize for comparison
            normalized = point.lower().strip()
            # Remove common prefixes
            for prefix in ['the ', 'a ', 'an ']:
                if normalized.startswith(prefix):
                    normalized = normalized[len(prefix):]

            # Check if similar exists (simple check - first 50 chars)
            key = normalized[:50]
            if key not in seen_normalized:
                seen_normalized.add(key)
                unique.append(point)

        return unique

    async def _check_objective_satisfaction(self) -> int:
        """Check how well accumulated points satisfy the original objective.

        Returns:
            Satisfaction percentage (0-100)
        """
        if not self.accumulated_points:
            return 0

        # Sample points for the prompt (max 20)
        sample_points = self.accumulated_points[:20]
        points_text = "\n".join(f"- {p}" for p in sample_points)

        prompt = f"""Evaluate how well these research findings satisfy the original objective.

**ORIGINAL OBJECTIVE:**
{self.base_topic}

**KEY FINDINGS ({len(self.accumulated_points)} total, showing first {len(sample_points)}):**
{points_text}

**TASK:**
Rate from 0-100 how completely these findings address the original objective.
- 0-30: Barely addresses the objective
- 31-50: Partially addresses, missing major aspects
- 51-70: Reasonably addresses, some gaps remain
- 71-85: Well addressed, minor gaps
- 86-100: Comprehensively addressed

**OUTPUT:**
Return ONLY a single number (0-100) representing your rating.
No other text, just the number."""

        try:
            response = await self.agent.research(prompt)
            # Extract number from response
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                score = int(numbers[0])
                return min(100, max(0, score))
            return 50  # Default if parsing fails
        except Exception as e:
            logger.warning(f"Failed to check objective satisfaction: {e}")
            return 50

    async def _generate_conclusion(self) -> Path:
        """Generate final conclusion document.

        Returns:
            Path to conclusion file
        """
        print("\n" + "=" * 50)
        print("GENERATING CONCLUSION")
        print("=" * 50)

        # Get top sources from KB
        top_domains = self.source_kb.get_top_domains(10)
        kb_stats = self.source_kb.get_search_term_stats()

        # Prepare points for prompt (max 50)
        points_for_prompt = self.accumulated_points[:50]
        points_text = "\n".join(f"- {p}" for p in points_for_prompt)

        prompt = f"""Generate a comprehensive CONCLUSION document for this research.

**ORIGINAL RESEARCH OBJECTIVE:**
{self.base_topic}

**KEY FINDINGS ({len(self.accumulated_points)} points accumulated):**
{points_text}

**RESEARCH STATISTICS:**
- Versions analyzed: {len(self.processed_versions)}
- Total sources found: {self.source_kb.get_sources_count()}
- Total searches performed: {kb_stats['total_searches']}
- Average search effectiveness: {kb_stats['avg_score']:.1f}%

**TASK:**
Write a well-structured conclusion document that:
1. Summarizes the key findings
2. Answers the original research objective
3. Highlights the most important insights
4. Notes any limitations or gaps
5. Provides actionable recommendations
6. Suggests areas for further research

**FORMAT:**
Use clear markdown formatting with:
- Executive Summary at the top
- Main sections with headers
- Bullet points for key items
- A "Recommendations" section
- A "Further Research" section

Write in a professional, clear style. The conclusion should stand alone as a complete summary of the research."""

        print("Generating with AI...", flush=True)

        try:
            conclusion_content = await self.agent.research(prompt)

            # Add metadata header
            timestamp = datetime.now().isoformat()
            header = f"""<!-- RESEARCH CONCLUSION -->
<!-- Research ID: {self.research_id} -->
<!-- Generated: {timestamp} -->
<!-- Versions Analyzed: {sorted(self.processed_versions)} -->
<!-- Key Points: {len(self.accumulated_points)} -->
<!-- Objective Satisfaction: {self.objective_satisfaction}% -->

---

# Research Conclusion

**Original Objective:** {self.base_topic}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

"""
            full_content = header + conclusion_content

            # Add sources appendix
            sources_appendix = self._generate_sources_appendix()
            full_content += sources_appendix

            # Save to file
            filename = f"conclusion-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
            filepath = self.conclusion_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)

            print(f"\nConclusion saved to: {filepath}")
            print(f"Length: {len(full_content)} characters")

            return filepath

        except Exception as e:
            logger.error(f"Failed to generate conclusion: {e}")
            print(f"\nError generating conclusion: {e}")
            return None

    def _generate_sources_appendix(self) -> str:
        """Generate sources appendix from KB.

        Returns:
            Markdown formatted sources section
        """
        appendix = "\n\n---\n\n# Appendix: Sources\n\n"

        # Top domains
        top_domains = self.source_kb.get_top_domains(15)
        if top_domains:
            appendix += "## Top Source Domains\n\n"
            for d in top_domains:
                appendix += f"- **{d['domain']}**: {d['count']} sources\n"

        # Best search terms
        stats = self.source_kb.get_search_term_stats()
        if stats['best_terms']:
            appendix += "\n## Most Effective Search Terms\n\n"
            for t in stats['best_terms'][:10]:
                appendix += f"- \"{t['term']}\" ({t['score']:.0f}% effectiveness)\n"

        # Language performance
        if stats.get('language_performance'):
            appendix += "\n## Search Performance by Language\n\n"
            for lang in stats['language_performance'][:8]:
                appendix += f"- **{lang['language'].upper()}**: {lang['count']} searches, {lang['avg_score']:.0f}% avg\n"

        appendix += f"\n\n*Total unique sources in knowledge base: {self.source_kb.get_sources_count()}*\n"

        return appendix
