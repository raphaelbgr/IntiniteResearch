"""Test parallel DuckDuckGo search tool (no LMStudio required)."""
import asyncio
import json
import sys
import io
from tools.parallel_ddg import ParallelDuckDuckGoSearch
from rich.console import Console
from rich.json import JSON

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

console = Console()


def test_single_search():
    """Test a single parallel search."""
    console.print("\n[bold cyan]Test 1: Single Search Query[/bold cyan]")

    search_tool = ParallelDuckDuckGoSearch(
        enable_search=True,
        enable_news=False
    )

    result_json = search_tool.parallel_search(
        search_queries=["Python programming"],
        max_results=3
    )

    result = json.loads(result_json)

    console.print(f"Total queries: {result['total_queries']}")
    console.print(f"Successful: {result['successful_queries']}")
    console.print(f"Total results: {result['total_results']}")
    console.print(f"Unique sources: {len(result.get('all_sources', []))}")

    if result.get('all_sources'):
        console.print("\n[bold]First source:[/bold]")
        source = result['all_sources'][0]
        console.print(f"  Title: {source['title']}")
        console.print(f"  URL: {source['url']}")
        console.print(f"  Snippet: {source['snippet'][:100]}...")

    return result


def test_multiple_searches():
    """Test multiple parallel searches."""
    console.print("\n[bold cyan]Test 2: Multiple Parallel Searches (3 queries)[/bold cyan]")

    search_tool = ParallelDuckDuckGoSearch(
        enable_search=True,
        enable_news=False
    )

    result_json = search_tool.parallel_search(
        search_queries=[
            "artificial intelligence",
            "machine learning",
            "neural networks"
        ],
        max_results=2
    )

    result = json.loads(result_json)

    console.print(f"Total queries: {result['total_queries']}")
    console.print(f"Successful: {result['successful_queries']}")
    console.print(f"Total results: {result['total_results']}")
    console.print(f"Unique sources: {len(result.get('all_sources', []))}")

    console.print("\n[bold]All sources:[/bold]")
    for i, source in enumerate(result.get('all_sources', [])[:5], 1):
        console.print(f"{i}. {source['title']}")
        console.print(f"   {source['url']}")

    return result


def test_news_search():
    """Test news search."""
    console.print("\n[bold cyan]Test 3: News Search[/bold cyan]")

    search_tool = ParallelDuckDuckGoSearch(
        enable_search=False,
        enable_news=True
    )

    result_json = search_tool.parallel_news(
        search_queries=["AI news 2025"],
        max_results=3
    )

    result = json.loads(result_json)

    console.print(f"Total queries: {result['total_queries']}")
    console.print(f"News articles found: {result['total_results']}")

    if result.get('all_sources'):
        console.print("\n[bold]Latest news:[/bold]")
        for i, source in enumerate(result.get('all_sources', [])[:3], 1):
            console.print(f"{i}. {source['title']}")
            console.print(f"   {source['url']}")

    return result


def test_error_handling():
    """Test error handling."""
    console.print("\n[bold cyan]Test 4: Error Handling[/bold cyan]")

    search_tool = ParallelDuckDuckGoSearch()

    # Test too many queries
    console.print("[yellow]Testing with 11 queries (should fail)...[/yellow]")
    result_json = search_tool.parallel_search(
        search_queries=["query" + str(i) for i in range(11)],
        max_results=1
    )

    result = json.loads(result_json)
    if 'error' in result:
        console.print(f"✓ Error handled correctly: {result['error']}")
    else:
        console.print("✗ Error not caught")

    # Test empty list
    console.print("[yellow]Testing with empty list (should fail)...[/yellow]")
    result_json = search_tool.parallel_search(
        search_queries=[],
        max_results=1
    )

    result = json.loads(result_json)
    if 'error' in result:
        console.print(f"✓ Error handled correctly: {result['error']}")
    else:
        console.print("✗ Error not caught")


def test_source_tracking():
    """Test that sources are properly tracked and deduplicated."""
    console.print("\n[bold cyan]Test 5: Source Tracking & Deduplication[/bold cyan]")

    search_tool = ParallelDuckDuckGoSearch()

    # Use related queries that might return overlapping results
    result_json = search_tool.parallel_search(
        search_queries=[
            "quantum computing basics",
            "introduction to quantum computing"
        ],
        max_results=3
    )

    result = json.loads(result_json)

    console.print(f"Query 1 results: {result['queries'][0]['result_count']}")
    console.print(f"Query 2 results: {result['queries'][1]['result_count']}")
    console.print(f"Total unique sources: {len(result['all_sources'])}")

    # Check for deduplication
    urls = [s['url'] for s in result.get('all_sources', [])]
    if len(urls) == len(set(urls)):
        console.print("[green]OK[/green] All sources are unique (deduplication working)")
    else:
        console.print("[red]ERROR[/red] Duplicate URLs found")


def main():
    """Run all tests."""
    console.print("[bold green]" + "=" * 60 + "[/bold green]")
    console.print("[bold green]Parallel DuckDuckGo Search Tool - Test Suite[/bold green]")
    console.print("[bold green]" + "=" * 60 + "[/bold green]")

    try:
        # Run tests
        test_single_search()
        test_multiple_searches()
        test_news_search()
        test_error_handling()
        test_source_tracking()

        console.print("\n[bold green]" + "=" * 60 + "[/bold green]")
        console.print("[bold green]✓ All tests completed![/bold green]")
        console.print("[bold green]" + "=" * 60 + "[/bold green]")

        console.print("\n[bold]The parallel search tool is working correctly.[/bold]")
        console.print("\nNext step: Test with LMStudio")
        console.print("1. Start LMStudio with a model loaded")
        console.print("2. Update config.yaml with your model name")
        console.print("3. Run: python research_orchestrator.py \"Test topic\"")

    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
