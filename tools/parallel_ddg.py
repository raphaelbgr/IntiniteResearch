r"""
Parallel DuckDuckGo Search Tool - Following Agno's DuckDuckGoTools pattern
Based on: C:\Users\rbgnr\git\agno\libs\agno\agno\tools\duckduckgo.py
"""
import json
import asyncio
import time
from typing import List, Optional, Any
from agno.tools import Toolkit
from agno.utils.log import log_debug
from utils.logger import get_logger

# NOTE: UTF-8 encoding is configured in research_orchestrator.py (entry point)

logger = get_logger()

try:
    from ddgs import DDGS
except ImportError:
    raise ImportError("`ddgs` not installed. Please install using `pip install ddgs`")


class ParallelDuckDuckGoSearch(Toolkit):
    """
    Parallel DuckDuckGo search toolkit - executes up to 25 searches simultaneously.

    Based on Agno's DuckDuckGoTools but adds parallel execution capability.
    Returns structured JSON with all sources automatically included.

    Args:
        enable_search (bool): Enable parallel web search
        enable_news (bool): Enable parallel news search
        backend (str): DuckDuckGo backend to use
        fixed_max_results (Optional[int]): Fixed number of results per query
        proxy (Optional[str]): Proxy for requests
        timeout (Optional[int]): Timeout per search (default: 10s)
    """

    # Class-level storage for last search results (accessible from outside)
    last_search_queries: List[str] = []
    last_search_performance: List[dict] = []
    last_sources: List[dict] = []

    def __init__(
        self,
        enable_search: bool = True,
        enable_news: bool = True,
        backend: str = "duckduckgo",
        fixed_max_results: Optional[int] = None,
        proxy: Optional[str] = None,
        timeout: Optional[int] = 10,
        verify_ssl: bool = True,
        **kwargs,
    ):
        self.proxy: Optional[str] = proxy
        self.timeout: Optional[int] = timeout
        self.fixed_max_results: Optional[int] = fixed_max_results
        self.verify_ssl: bool = verify_ssl
        self.backend: str = backend

        tools: List[Any] = []
        if enable_search:
            tools.append(self.parallel_search)
        if enable_news:
            tools.append(self.parallel_news)

        super().__init__(name="parallel_duckduckgo", tools=tools, **kwargs)

    @classmethod
    def get_last_search_data(cls) -> dict:
        """Get data from last search for saving in refinement metadata."""
        return {
            'queries': cls.last_search_queries.copy(),
            'performance': cls.last_search_performance.copy(),
            'sources': cls.last_sources.copy()
        }

    def _sanitize_query(self, query: str) -> str:
        """Sanitize and trim query to reasonable length.

        Args:
            query: Raw search query

        Returns:
            Sanitized query (max self.max_query_words words, deduplicated)
        """
        if not query or not isinstance(query, str):
            return ""

        # Split into words
        words = query.split()

        # Remove duplicate consecutive words (like "analysis analysis analysis")
        deduped_words = []
        prev_word = None
        for word in words:
            if word.lower() != prev_word:
                deduped_words.append(word)
                prev_word = word.lower()

        # Take only first N words
        trimmed_words = deduped_words[:self.max_query_words]

        result = " ".join(trimmed_words)
        log_debug(f"Sanitized query: '{query[:50]}...' -> '{result}'")

        return result

    def _sanitize_queries(self, queries: List[str]) -> List[str]:
        """Sanitize list of queries.

        Args:
            queries: List of raw search queries

        Returns:
            List of sanitized queries (duplicates removed)
        """
        sanitized = []
        seen = set()

        for q in queries:
            clean = self._sanitize_query(q)
            if clean and clean.lower() not in seen:
                sanitized.append(clean)
                seen.add(clean.lower())

        return sanitized

    def parallel_search(
        self,
        search_queries: List[str],
        max_results: Optional[int] = 5
    ) -> str:
        """
        Execute multiple DuckDuckGo web searches in parallel.

        Generate 20 search term variations and search ALL of them simultaneously!
        Queries can be any length - mix of English and multilingual terms.

        Args:
            search_queries: List of 20 search queries (English + multilingual variations).
                           Generate variations in different languages for global coverage.
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

        # NO FILTERING - use all queries as-is from AI

        actual_max_results = self.fixed_max_results or max_results

        log_debug(
            f"Executing {len(search_queries)} parallel DDG searches "
            f"with {actual_max_results} results each"
        )

        # Run searches in parallel using asyncio
        start_time = time.time()
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, need to use create_task or gather
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_searches_sync, search_queries, actual_max_results)
                    results = future.result()
            except RuntimeError:
                # No running loop, create new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    self._execute_parallel_searches(search_queries, actual_max_results)
                )
                loop.close()

            # Calculate stats and log summary
            elapsed_ms = int((time.time() - start_time) * 1000)
            json_result = json.dumps(results, indent=2)
            content_kb = len(json_result.encode('utf-8')) / 1024

            # Print detailed per-query results
            print(f"\n{'='*70}")
            print(f"🔍 DDG SEARCH COMPLETE - {elapsed_ms}ms | {content_kb:.1f}KB")
            print(f"{'='*70}")

            # Show results per query and save to class storage
            queries_data = results.get('queries', [])
            total_results = 0
            ParallelDuckDuckGoSearch.last_search_queries = []
            ParallelDuckDuckGoSearch.last_search_performance = []

            for i, q_data in enumerate(queries_data, 1):
                query = q_data.get('query', 'unknown')
                count = len(q_data.get('results', []))
                total_results += count
                # Calculate success score (0-100%)
                score = min(100, count * 20)  # 5 results = 100%
                bar = '█' * (score // 10) + '░' * (10 - score // 10)
                print(f"  {i:2d}. [{bar}] {score:3d}% | {count} results | {query[:60]}")

                # Save to class storage for metadata
                ParallelDuckDuckGoSearch.last_search_queries.append(query)
                ParallelDuckDuckGoSearch.last_search_performance.append({
                    'term': query,
                    'results': count,
                    'score': score
                })

            # Save sources
            ParallelDuckDuckGoSearch.last_sources = results.get('all_sources', [])

            print(f"{'─'*70}")
            # Extract and display domains
            domains = {}
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

            return json_result

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            print(f"\n❌ DDG Search FAILED after {elapsed_ms}ms: {e}\n")
            return json.dumps({"error": str(e)})

    def _run_searches_sync(self, queries: List[str], max_results: int) -> dict:
        """Run searches synchronously (for when called from async context)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                self._execute_parallel_searches(queries, max_results)
            )
            return results
        finally:
            loop.close()

    async def _execute_parallel_searches(
        self,
        queries: List[str],
        max_results: int
    ) -> dict:
        """Execute searches in parallel."""
        tasks = [
            self._search_single(query, max_results)
            for query in queries
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build response following Agno's JSON pattern
        # ddgs.text() returns: [{"title": str, "href": str, "body": str}, ...]
        response = {
            "total_queries": len(queries),
            "successful_queries": 0,
            "total_results": 0,
            "all_sources": [],  # All unique sources across all queries
            "queries": []
        }

        seen_urls = set()

        for query, result in zip(queries, results):
            if isinstance(result, Exception):
                response["queries"].append({
                    "query": query,
                    "status": "failed",
                    "error": str(result),
                    "results": []
                })
            else:
                # Extract sources from DDGS result format
                # DDGS returns: {"title", "href", "body"}
                for item in result:
                    url = item.get("href", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        response["all_sources"].append({
                            "title": item.get("title", "Unknown"),
                            "url": url,
                            "snippet": item.get("body", "")[:200]
                        })

                response["queries"].append({
                    "query": query,
                    "status": "success",
                    "result_count": len(result),
                    "results": result  # Keep original DDGS format
                })
                response["successful_queries"] += 1
                response["total_results"] += len(result)

        return response

    async def _search_single(self, query: str, max_results: int) -> List[dict]:
        """Execute a single search (async wrapper for sync DDGS)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._ddgs_search_sync,
            query,
            max_results
        )

    def _ddgs_search_sync(self, query: str, max_results: int) -> List[dict]:
        """Synchronous DDGS search (following Agno's pattern)."""
        try:
            log_debug(f"Searching DDG for: {query} using backend: {self.backend}")
            with DDGS(
                proxy=self.proxy,
                timeout=self.timeout,
                verify=self.verify_ssl
            ) as ddgs:
                # Returns list of dicts: [{"title", "href", "body"}, ...]
                results = list(ddgs.text(
                    query=query,
                    max_results=max_results,
                    backend=self.backend
                ))
                return results
        except Exception as e:
            log_debug(f"Search failed for '{query}': {e}")
            return []

    def parallel_news(
        self,
        search_queries: List[str],
        max_results: Optional[int] = 5
    ) -> str:
        """
        Execute multiple DuckDuckGo NEWS searches in parallel.

        Generate 20 search term variations and search ALL of them simultaneously!
        Queries can be any length - mix of English and multilingual terms.

        Args:
            search_queries: List of 20 news search queries (English + multilingual).
                           Generate variations in different languages for global news.
            max_results: Results per query (default: 5)

        Returns:
            JSON with news results including per-query stats for performance tracking.
        """
        if not isinstance(search_queries, list):
            return json.dumps({"error": "search_queries must be a list"})

        if len(search_queries) == 0 or len(search_queries) > 25:
            return json.dumps({"error": "Need 1-25 search queries"})

        # NO FILTERING - use all queries as-is from AI

        actual_max_results = self.fixed_max_results or max_results

        log_debug(f"Executing {len(search_queries)} parallel DDG news searches")

        start_time = time.time()
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_news_sync, search_queries, actual_max_results)
                    results = future.result()
            except RuntimeError:
                # No running loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    self._execute_parallel_news(search_queries, actual_max_results)
                )
                loop.close()

            # Calculate stats and log summary
            elapsed_ms = int((time.time() - start_time) * 1000)
            json_result = json.dumps(results, indent=2)
            content_kb = len(json_result.encode('utf-8')) / 1024

            # Print detailed per-query results
            print(f"\n{'='*70}")
            print(f"📰 DDG NEWS COMPLETE - {elapsed_ms}ms | {content_kb:.1f}KB")
            print(f"{'='*70}")

            # Show results per query and save to class storage
            queries_data = results.get('queries', [])
            total_results = 0
            ParallelDuckDuckGoSearch.last_search_queries = []
            ParallelDuckDuckGoSearch.last_search_performance = []

            for i, q_data in enumerate(queries_data, 1):
                query = q_data.get('query', 'unknown')
                count = len(q_data.get('results', []))
                total_results += count
                # Calculate success score (0-100%)
                score = min(100, count * 20)  # 5 results = 100%
                bar = '█' * (score // 10) + '░' * (10 - score // 10)
                print(f"  {i:2d}. [{bar}] {score:3d}% | {count} results | {query[:60]}")

                # Save to class storage for metadata
                ParallelDuckDuckGoSearch.last_search_queries.append(query)
                ParallelDuckDuckGoSearch.last_search_performance.append({
                    'term': query,
                    'results': count,
                    'score': score
                })

            # Save sources
            ParallelDuckDuckGoSearch.last_sources = results.get('all_sources', [])

            print(f"{'─'*70}")
            # Extract and display domains
            domains = {}
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

            return json_result

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            print(f"\n❌ DDG News FAILED after {elapsed_ms}ms: {e}\n")
            return json.dumps({"error": str(e)})

    def _run_news_sync(self, queries: List[str], max_results: int) -> dict:
        """Run news searches synchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                self._execute_parallel_news(queries, max_results)
            )
            return results
        finally:
            loop.close()

    async def _execute_parallel_news(
        self,
        queries: List[str],
        max_results: int
    ) -> dict:
        """Execute news searches in parallel."""
        tasks = [
            self._news_search_single(query, max_results)
            for query in queries
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Same structure as regular search
        response = {
            "total_queries": len(queries),
            "successful_queries": 0,
            "total_results": 0,
            "all_sources": [],
            "queries": []
        }

        seen_urls = set()

        for query, result in zip(queries, results):
            if isinstance(result, Exception):
                response["queries"].append({
                    "query": query,
                    "status": "failed",
                    "error": str(result),
                    "results": []
                })
            else:
                # DDGS news format: {"title", "url", "body", "date", "source"}
                for item in result:
                    url = item.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        response["all_sources"].append({
                            "title": item.get("title", "Unknown"),
                            "url": url,
                            "snippet": item.get("body", "")[:200]
                        })

                response["queries"].append({
                    "query": query,
                    "status": "success",
                    "result_count": len(result),
                    "results": result
                })
                response["successful_queries"] += 1
                response["total_results"] += len(result)

        return response

    async def _news_search_single(self, query: str, max_results: int) -> List[dict]:
        """Execute a single news search."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._ddgs_news_sync,
            query,
            max_results
        )

    def _ddgs_news_sync(self, query: str, max_results: int) -> List[dict]:
        """Synchronous DDGS news search."""
        try:
            log_debug(f"Searching DDG news for: {query}")
            with DDGS(
                proxy=self.proxy,
                timeout=self.timeout,
                verify=self.verify_ssl
            ) as ddgs:
                results = list(ddgs.news(
                    query=query,
                    max_results=max_results
                ))
                return results
        except Exception as e:
            log_debug(f"News search failed for '{query}': {e}")
            return []
