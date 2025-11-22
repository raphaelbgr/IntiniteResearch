"""Context manager for optimizing weak model performance."""
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from utils.logger import get_logger

# NOTE: UTF-8 encoding is configured in research_orchestrator.py (entry point)

logger = get_logger()


class ContextManager:
    """Manages context for weak models - last 2 refinements only."""

    def __init__(self):
        """Initialize context manager."""
        pass

    def extract_search_terms(self, refinement_content: str) -> List[str]:
        """Extract search terms from refinement metadata.

        Args:
            refinement_content: Content of refinement file

        Returns:
            List of search terms used
        """
        # Look for search terms section at top of file
        search_terms = []

        # Match pattern: <!-- SEARCH_TERMS: term1, term2, term3 -->
        pattern = r'<!-- SEARCH_TERMS:\s*(.+?)\s*-->'
        match = re.search(pattern, refinement_content, re.MULTILINE)

        if match:
            terms_str = match.group(1)
            search_terms = [t.strip() for t in terms_str.split(',') if t.strip()]

        logger.debug(f"Extracted {len(search_terms)} search terms")

        return search_terms

    def extract_sources(self, refinement_content: str) -> List[Dict[str, str]]:
        """Extract source URLs from refinement metadata.

        Args:
            refinement_content: Content of refinement file

        Returns:
            List of source dictionaries with url and title
        """
        sources = []

        # Match pattern: SOURCE: title | url (within SOURCES comment block)
        # Look for the SOURCES block first
        sources_block_pattern = r'<!--\s*SOURCES:(.*?)-->'
        sources_match = re.search(sources_block_pattern, refinement_content, re.DOTALL)

        if sources_match:
            sources_block = sources_match.group(1)
            # Now extract individual SOURCE lines
            source_pattern = r'SOURCE:\s*(.+?)\s*\|\s*(.+?)(?:\n|$)'
            matches = re.findall(source_pattern, sources_block, re.MULTILINE)

            for title, url in matches:
                sources.append({
                    'title': title.strip(),
                    'url': url.strip()
                })

        logger.debug(f"Extracted {len(sources)} sources")

        return sources

    def format_refinement_with_metadata(
        self,
        content: str,
        search_terms: List[str],
        version: int,
        research_id: str,
        sources_count: int = 0,
        search_performance: Optional[List[Dict[str, Any]]] = None,
        kb_summary: Optional[str] = None
    ) -> str:
        """Format refinement with metadata at top.

        Args:
            content: Main document content
            search_terms: Search terms used in this iteration
            version: Refinement version number
            research_id: Research session ID
            sources_count: Number of sources found (stored in KB, not here)
            search_performance: Optional list of {term, results, score} for each search
            kb_summary: Optional summary from SourceKnowledgeBase

        Returns:
            Formatted content with metadata
        """
        metadata_parts = [
            f"<!-- RESEARCH_ID: {research_id} -->",
            f"<!-- VERSION: {version:04d} -->",
            f"<!-- SEARCH_TERMS: {', '.join(search_terms)} -->",
            f"<!-- SOURCES_COUNT: {sources_count} (stored in Knowledge Base) -->",
        ]

        # Add search performance data for AI to analyze and improve
        if search_performance:
            metadata_parts.append("<!--")
            metadata_parts.append("SEARCH_PERFORMANCE (use this to improve next search terms):")
            total_results = 0
            for perf in search_performance:
                term = perf.get('term', 'unknown')
                results = perf.get('results', 0)
                score = perf.get('score', 0)
                total_results += results
                metadata_parts.append(f"  TERM: {term} | RESULTS: {results} | SCORE: {score}%")
            avg_score = sum(p.get('score', 0) for p in search_performance) / len(search_performance) if search_performance else 0
            metadata_parts.append(f"  AVERAGE_SCORE: {avg_score:.0f}%")
            metadata_parts.append(f"  TOTAL_RESULTS: {total_results}")
            metadata_parts.append("  GUIDANCE: If scores are low (<50%), try different keyword combinations.")
            metadata_parts.append("  GUIDANCE: High-scoring terms can be varied for deeper research.")
            metadata_parts.append("-->")

        # Add KB summary if provided (minimal reference, full data in KB)
        if kb_summary:
            metadata_parts.append("<!--")
            metadata_parts.append("KNOWLEDGE_BASE_SUMMARY:")
            for line in kb_summary.split('\n'):
                metadata_parts.append(f"  {line}")
            metadata_parts.append("-->")

        metadata_parts.extend(["", "---", ""])

        formatted = "\n".join(metadata_parts) + content

        return formatted

    def generate_search_variations(
        self,
        base_topic: str,
        previous_searches: List[str],
        iteration: int
    ) -> List[str]:
        """Returns empty list - AI generates its own 20 search terms.

        NO FILTERING - the AI is instructed to generate 20 search term
        variations and use ALL of them in parallel searches.

        Args:
            base_topic: Original research topic (passed to AI, not used here)
            previous_searches: Not used
            iteration: Not used

        Returns:
            Empty list - AI generates search terms
        """
        # NO FILTERING - AI generates 20 search terms itself
        print(f"📝 Topic passed to AI (no filtering): '{base_topic[:80]}...'")
        print("🤖 AI will generate 20 search term variations")

        # Return empty - AI handles search term generation
        return []

    def generate_search_variations_legacy(
        self,
        base_topic: str,
        previous_searches: List[str],
        iteration: int
    ) -> List[str]:
        """LEGACY - not used. Kept for reference."""
        lang_keys = []
        start_lang_idx = (iteration - 1) % len(lang_keys)

        multilingual_count = 0
        lang_idx = start_lang_idx

        while multilingual_count < 15:
            lang = lang_keys[lang_idx % len(lang_keys)]
            modifiers_list = multilingual_modifiers[lang]

            modifier_idx = (iteration + lang_idx) % len(modifiers_list)
            modifier = modifiers_list[modifier_idx]

            query = f"{core_topic} {modifier}"

            if query not in previous_searches and query not in variations:
                variations.append(query)
                multilingual_count += 1

            lang_idx += 1
            if lang_idx > start_lang_idx + 30:
                break

        print(f"🔎 Generated {len(variations)} search queries (5 EN + 15 multilingual)")

        return variations[:20]

    async def load_last_refinements(
        self,
        file_manager,
        research_id: str,
        n: int = 2
    ) -> List[Dict[str, Any]]:
        """Load last N refinement files.

        Args:
            file_manager: FileManager instance
            research_id: Research session ID
            n: Number of refinements to load (default: 2)

        Returns:
            List of refinement data (content, version, search_terms)
        """
        latest_version = file_manager.get_latest_version(research_id)

        if latest_version == 0:
            return []

        refinements = []

        # Load last N versions
        for version in range(max(1, latest_version - n + 1), latest_version + 1):
            content = await file_manager.load_refinement(research_id, version)

            if content:
                search_terms = self.extract_search_terms(content)

                refinements.append({
                    'version': version,
                    'content': content,
                    'search_terms': search_terms
                })

        logger.info(f"Loaded {len(refinements)} previous refinement(s)")

        return refinements

    def build_context_prompt(
        self,
        base_prompt: str,
        previous_refinements: List[Dict[str, Any]],
        input_files_content: str = ""
    ) -> str:
        """Build context prompt with last 2 refinements.

        Args:
            base_prompt: Base research or refinement prompt
            previous_refinements: Last 2 refinement data
            input_files_content: Optional input files content

        Returns:
            Complete prompt with context
        """
        parts = []

        # Add input files if provided
        if input_files_content:
            parts.append("# User-Provided Input Files\n")
            parts.append(input_files_content)
            parts.append("\n---\n\n")

        # Add previous refinements
        if previous_refinements:
            parts.append("# Previous Research Iterations\n")
            parts.append(
                "*Review these previous iterations to understand what has been covered "
                "and what needs improvement or expansion.*\n\n"
            )

            for ref in previous_refinements:
                parts.append(f"## Previous Iteration (Version {ref['version']})\n\n")

                if ref['search_terms']:
                    parts.append("**Search Terms Used:**\n")
                    for term in ref['search_terms']:
                        parts.append(f"- {term}\n")
                    parts.append("\n")

                # Include content but limit size for weak models
                content = ref['content']

                # Remove metadata from content display
                content = re.sub(
                    r'<!-- .+? -->',
                    '',
                    content,
                    flags=re.DOTALL
                ).strip()

                # Limit to first 2000 chars if too long
                if len(content) > 2000:
                    content = content[:2000] + "\n\n*[Content truncated for context efficiency]*"

                parts.append(content)
                parts.append("\n\n---\n\n")

        # Add current task
        parts.append("# Current Task\n\n")
        parts.append(base_prompt)

        return "".join(parts)

    def extract_research_gaps(
        self,
        refinements: List[Dict[str, Any]]
    ) -> List[str]:
        """Analyze refinements to identify research gaps.

        Args:
            refinements: Previous refinement data

        Returns:
            List of identified gaps or areas needing more research
        """
        gaps = []

        # Simple heuristic: look for TODO, FIXME, or sections that are short
        for ref in refinements:
            content = ref['content']

            # Find TODO/FIXME markers
            todo_pattern = r'(?:TODO|FIXME|TBD):\s*(.+?)(?:\n|$)'
            todos = re.findall(todo_pattern, content, re.IGNORECASE)
            gaps.extend(todos)

            # Find very short sections (potential gaps)
            section_pattern = r'##\s+(.+?)\n\n(.+?)(?=\n##|\Z)'
            sections = re.findall(section_pattern, content, re.DOTALL)

            for title, section_content in sections:
                if len(section_content.strip()) < 200:
                    gaps.append(f"Expand section: {title.strip()}")

        # Limit and deduplicate
        gaps = list(dict.fromkeys(gaps))[:5]

        return gaps
