"""Custom tools for Infinite Research system."""

import os
from .parallel_ddg import ParallelDuckDuckGoSearch

try:
    from .tavily_search import TavilySearch
    _TAVILY_AVAILABLE = True
except ImportError:
    TavilySearch = None  # type: ignore
    _TAVILY_AVAILABLE = False

__all__ = ['ParallelDuckDuckGoSearch', 'TavilySearch', 'get_aggregated_search_data']


def _empty_search_data() -> dict:
    """Return an empty search-data envelope."""
    return {'queries': [], 'performance': [], 'sources': []}


def get_aggregated_search_data() -> dict:
    """Aggregate search metadata from whichever provider(s) are active.

    Checks SEARCH_PROVIDER env var and merges class-level state from the
    active provider(s). When provider is 'both', data from both DDG and
    Tavily are combined.

    Returns:
        dict with keys 'queries', 'performance', 'sources'.
    """
    provider = os.environ.get("SEARCH_PROVIDER", "duckduckgo")

    ddg_data = ParallelDuckDuckGoSearch.get_last_search_data()

    if _TAVILY_AVAILABLE:
        tavily_data = TavilySearch.get_last_search_data()
    else:
        tavily_data = _empty_search_data()
        if provider in ("tavily", "both"):
            from utils.logger import get_logger
            get_logger().warning(
                "SEARCH_PROVIDER is '%s' but tavily-python is not installed; "
                "Tavily data will be empty.",
                provider,
            )

    if provider == "tavily":
        return tavily_data
    elif provider == "both":
        # Merge both: concatenate lists, dedup sources by URL
        merged_queries = ddg_data['queries'] + tavily_data['queries']
        merged_performance = ddg_data['performance'] + tavily_data['performance']

        seen_urls = set()
        merged_sources = []
        for src in ddg_data['sources'] + tavily_data['sources']:
            url = src.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                merged_sources.append(src)

        return {
            'queries': merged_queries,
            'performance': merged_performance,
            'sources': merged_sources,
        }
    else:
        # Default: duckduckgo
        return ddg_data
