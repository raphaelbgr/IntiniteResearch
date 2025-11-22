"""Proper source tracking using Agno's structured outputs and DuckDuckGo's native format."""
from typing import List, Dict, Any, Optional
import json
from models.research_models import SearchSource
from utils.logger import get_logger

logger = get_logger()


class SourceTracker:
    """Track sources from DuckDuckGo search results (already structured!)."""

    @staticmethod
    def extract_from_parallel_search(search_result_json: str) -> List[SearchSource]:
        """Extract sources from parallel search tool output.

        The parallel_search tool already returns structured JSON with sources!
        No need for regex parsing - just use the structured data.

        Args:
            search_result_json: JSON string from parallel_search tool

        Returns:
            List of SearchSource objects
        """
        sources = []

        try:
            data = json.loads(search_result_json)

            # Our parallel search now includes 'all_sources' field
            if 'all_sources' in data:
                for source_dict in data['all_sources']:
                    try:
                        source = SearchSource(
                            title=source_dict.get('title', 'Unknown'),
                            url=source_dict.get('url', ''),
                            snippet=source_dict.get('snippet', '')
                        )
                        if source.url:
                            sources.append(source)
                    except Exception as e:
                        logger.debug(f"Failed to parse source: {e}")
                        continue

            # Fallback: parse queries array if all_sources not present
            elif 'queries' in data:
                for query_result in data['queries']:
                    if query_result.get('status') == 'success':
                        for result in query_result.get('results', []):
                            try:
                                source = SearchSource(
                                    title=result.get('title', 'Unknown'),
                                    url=result.get('href', result.get('url', '')),
                                    snippet=result.get('body', result.get('description', ''))[:200]
                                )
                                if source.url:
                                    sources.append(source)
                            except Exception as e:
                                logger.debug(f"Failed to parse source: {e}")
                                continue

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse search results JSON: {e}")
        except Exception as e:
            logger.error(f"Error extracting sources: {e}")

        # Deduplicate by URL
        unique_sources = {}
        for source in sources:
            if source.url not in unique_sources:
                unique_sources[source.url] = source

        result = list(unique_sources.values())
        logger.info(f"Extracted {len(result)} unique sources from search results")

        return result

    @staticmethod
    def sources_to_metadata_format(sources: List[SearchSource]) -> List[Dict[str, str]]:
        """Convert SearchSource objects to metadata dict format.

        Args:
            sources: List of SearchSource objects

        Returns:
            List of dicts with title and url
        """
        return [
            {"title": s.title, "url": s.url}
            for s in sources
        ]

    @staticmethod
    def format_sources_for_display(
        sources: List[SearchSource],
        max_display: int = 20
    ) -> str:
        """Format sources for display in document.

        Args:
            sources: List of SearchSource objects
            max_display: Maximum sources to display

        Returns:
            Formatted markdown string
        """
        if not sources:
            return ""

        lines = ["\n## Sources\n"]

        for i, source in enumerate(sources[:max_display], 1):
            lines.append(f"{i}. [{source.title}]({source.url})")

        if len(sources) > max_display:
            lines.append(f"\n*... and {len(sources) - max_display} more sources*")

        return "\n".join(lines)

    @staticmethod
    def get_unique_domains(sources: List[SearchSource]) -> List[str]:
        """Extract unique domains from sources.

        Args:
            sources: List of SearchSource objects

        Returns:
            List of unique domain names
        """
        import re

        domains = set()

        for source in sources:
            # Extract domain from URL
            match = re.search(r'https?://(?:www\.)?([^/]+)', source.url)
            if match:
                domains.add(match.group(1))

        return sorted(list(domains))
