r"""
Parallel Tavily Search Tool - Following Agno's Toolkit pattern
Mirrors the ParallelDuckDuckGoSearch interface for drop-in compatibility.
"""
import asyncio
import concurrent.futures
import json
import os
import time
from typing import List, Optional, Any
from agno.tools import Toolkit
from agno.utils.log import log_debug
from utils.logger import get_logger

logger = get_logger()

try:
    from tavily import TavilyClient, AsyncTavilyClient
except ImportError:
    raise ImportError("`tavily-python` not installed. Please install using `pip install tavily-python`")


class TavilySearch(Toolkit):
    """
    Parallel Tavily search toolkit - executes searches via the Tavily API.

    Returns the same JSON envelope structure as ParallelDuckDuckGoSearch
    so downstream code (refinement/refiner.py, source tracking) works uniformly.

    Args:
        enable_search (bool): Enable web search
        enable_news (bool): Enable news search
        api_key (Optional[str]): Tavily API key (falls back to TAVILY_API_KEY env var)
        fixed_max_results (Optional[int]): Fixed number of results per query
        search_depth (str): Tavily search depth ('basic' or 'advanced')
    """

    # Class-level storage for last search results (accessible from outside)
    last_search_queries: List[str] = []
    last_search_performance: List[dict] = []
    last_sources: List[dict] = []

    def __init__(
        self,
        enable_search: bool = True,
        enable_news: bool = True,
        api_key: Optional[str] = None,
        fixed_max_results: Optional[int] = None,
        search_depth: str = "basic",
        **kwargs,
    ):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "Tavily API key is required. Set TAVILY_API_KEY env var or pass api_key."
            )
        self.client = TavilyClient(api_key=self.api_key)
        self.fixed_max_results: Optional[int] = fixed_max_results
        self.search_depth: str = search_depth

        tools: List[Any] = []
        if enable_search:
            tools.append(self.parallel_search)
        if enable_news:
            tools.append(self.parallel_news)

        super().__init__(name="tavily_search", tools=tools, **kwargs)

    @classmethod
    def get_last_search_data(cls) -> dict:
        """Get data from last search for saving in refinement metadata."""
        return {
            'queries': cls.last_search_queries.copy(),
            'performance': cls.last_search_performance.copy(),
            'sources': cls.last_sources.copy()
        }

    def parallel_search(
        self,
        search_queries: List[str],
        max_results: Optional[int] = 5
    ) -> str:
        """
        Execute multiple Tavily web searches.

        Generate 20 search term variations and search ALL of them simultaneously!
        Queries can be any length - mix of English and multilingual terms.

        Args:
            search_queries: List of up to 25 search queries.
            max_results: Results per query (default: 5)

        Returns:
            JSON with results including per-query stats for performance tracking.
        """
        if not isinstance(search_queries, list):
            return json.dumps({"error": "search_queries must be a list"})

        if len(search_queries) == 0:
            return json.dumps({"error": "At least 1 search query required"})

        if len(search_queries) > 25:
            return json.dumps(
                {"error": "Maximum 25 parallel searches. Please reduce queries."}
            )

        actual_max_results = self.fixed_max_results or max_results

        log_debug(
            f"Executing {len(search_queries)} Tavily searches "
            f"with {actual_max_results} results each"
        )

        start_time = time.time()
        try:
            response = self._build_response(search_queries, actual_max_results, topic="general")

            elapsed_ms = int((time.time() - start_time) * 1000)
            json_result = json.dumps(response, indent=2)
            content_kb = len(json_result.encode('utf-8')) / 1024

            self._log_results(response, elapsed_ms, content_kb, label="TAVILY SEARCH")

            return json_result

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            print(f"\n❌ Tavily Search FAILED after {elapsed_ms}ms: {e}\n")
            return json.dumps({"error": str(e)})

    def parallel_news(
        self,
        search_queries: List[str],
        max_results: Optional[int] = 5
    ) -> str:
        """
        Execute multiple Tavily NEWS searches.

        Generate 20 search term variations and search ALL of them simultaneously!
        Queries can be any length - mix of English and multilingual terms.

        Args:
            search_queries: List of up to 25 news search queries.
            max_results: Results per query (default: 5)

        Returns:
            JSON with news results including per-query stats for performance tracking.
        """
        if not isinstance(search_queries, list):
            return json.dumps({"error": "search_queries must be a list"})

        if len(search_queries) == 0 or len(search_queries) > 25:
            return json.dumps({"error": "Need 1-25 search queries"})

        actual_max_results = self.fixed_max_results or max_results

        log_debug(f"Executing {len(search_queries)} Tavily news searches")

        start_time = time.time()
        try:
            response = self._build_response(search_queries, actual_max_results, topic="news")

            elapsed_ms = int((time.time() - start_time) * 1000)
            json_result = json.dumps(response, indent=2)
            content_kb = len(json_result.encode('utf-8')) / 1024

            self._log_results(response, elapsed_ms, content_kb, label="TAVILY NEWS")

            return json_result

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            print(f"\n❌ Tavily News FAILED after {elapsed_ms}ms: {e}\n")
            return json.dumps({"error": str(e)})

    def _build_response(
        self,
        queries: List[str],
        max_results: int,
        topic: str = "general"
    ) -> dict:
        """Execute queries via Tavily in parallel and build the standard response envelope."""
        try:
            loop = asyncio.get_running_loop()
            # Already in an async context — run in a thread to avoid blocking
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    self._run_parallel_searches_sync, queries, max_results, topic
                )
                return future.result()
        except RuntimeError:
            # No running loop — create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self._execute_parallel_searches(queries, max_results, topic)
                )
            finally:
                loop.close()

    def _run_parallel_searches_sync(
        self,
        queries: List[str],
        max_results: int,
        topic: str
    ) -> dict:
        """Run parallel Tavily searches from a sync context."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._execute_parallel_searches(queries, max_results, topic)
            )
        finally:
            loop.close()

    async def _execute_parallel_searches(
        self,
        queries: List[str],
        max_results: int,
        topic: str
    ) -> dict:
        """Execute all queries concurrently using AsyncTavilyClient."""
        async_client = AsyncTavilyClient(api_key=self.api_key)

        async def _search_one(query: str):
            log_debug(f"Searching Tavily for: {query} (topic={topic})")
            return await async_client.search(
                query=query,
                max_results=max_results,
                search_depth=self.search_depth,
                topic=topic,
            )

        tasks = [_search_one(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        response = {
            "total_queries": len(queries),
            "successful_queries": 0,
            "total_results": 0,
            "all_sources": [],
            "queries": []
        }

        seen_urls: set = set()

        for query, result in zip(queries, results):
            if isinstance(result, Exception):
                log_debug(f"Tavily search failed for '{query}': {result}")
                response["queries"].append({
                    "query": query,
                    "status": "failed",
                    "error": str(result),
                    "results": [],
                })
                continue

            items = result.get("results", [])
            normalized: List[dict] = []
            for item in items:
                url = item.get("url", "")
                title = item.get("title", "Unknown")
                snippet = item.get("content", "")[:200]

                normalized.append({
                    "title": title,
                    "href": url,
                    "body": item.get("content", ""),
                })

                if url and url not in seen_urls:
                    seen_urls.add(url)
                    response["all_sources"].append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    })

            response["queries"].append({
                "query": query,
                "status": "success",
                "result_count": len(normalized),
                "results": normalized,
            })
            response["successful_queries"] += 1
            response["total_results"] += len(normalized)

        return response

    def _log_results(self, results: dict, elapsed_ms: int, content_kb: float, label: str):
        """Log search results summary and update class-level storage."""
        print(f"\n{'='*70}")
        print(f"🔍 {label} COMPLETE - {elapsed_ms}ms | {content_kb:.1f}KB")
        print(f"{'='*70}")

        queries_data = results.get('queries', [])
        total_results = 0
        TavilySearch.last_search_queries = []
        TavilySearch.last_search_performance = []

        for i, q_data in enumerate(queries_data, 1):
            query = q_data.get('query', 'unknown')
            count = len(q_data.get('results', []))
            total_results += count
            score = min(100, count * 20)
            bar = '█' * (score // 10) + '░' * (10 - score // 10)
            print(f"  {i:2d}. [{bar}] {score:3d}% | {count} results | {query[:60]}")

            TavilySearch.last_search_queries.append(query)
            TavilySearch.last_search_performance.append({
                'term': query,
                'results': count,
                'score': score
            })

        TavilySearch.last_sources = results.get('all_sources', [])

        print(f"{'─'*70}")
        domains: dict = {}
        for source in results.get("all_sources", []):
            url = source.get("url", "")
            if url:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.replace("www.", "")
                domains[domain] = domains.get(domain, 0) + 1
        top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:8]
        domain_str = ", ".join([f"{d}({c})" for d, c in top_domains])
        print(f"  TOTAL: {total_results} results | {len(results.get('all_sources', []))} unique links")
        if domain_str:
            print(f"  DOMAINS: {domain_str}")
        print(f"{'='*70}\n")
