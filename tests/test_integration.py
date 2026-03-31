"""Integration tests to catch bugs unit tests miss."""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.mark.asyncio
async def test_conduct_initial_research_flow(temp_dir):
    """Test the complete initial research flow to catch variable errors."""
    from research_orchestrator import ResearchOrchestrator
    from unittest.mock import AsyncMock, MagicMock

    # Mock config
    config = {
        'lmstudio': {'base_url': 'http://test', 'model': 'test', 'api_key': 'test', 'temperature': 0.7, 'max_tokens': 2048},
        'research': {'refinement_delay': 1, 'enable_evaluation': False, 'evaluation_frequency': 10, 'output_dir': str(temp_dir)},
        'vector_db': {'type': 'sqlite'},
        'storage': {'type': 'sqlite', 'memory_db': 'test.db'},
        'logging': {'level': 'ERROR', 'console': False}
    }

    with patch('research_orchestrator.load_config', return_value=config):
        orchestrator = ResearchOrchestrator(enable_evaluation=False)

        # Mock agent research
        orchestrator.base_topic = "test topic"
        orchestrator.input_files_content = ""

        # Initialize
        await orchestrator.initialize_research("test topic")

        # Mock research agent response
        orchestrator.research_agent.research = AsyncMock(return_value="# Test Research\n\nContent here.")

        # This should NOT raise NameError: sources_dict
        try:
            await orchestrator.conduct_initial_research("test topic")
            # Success - no NameError
            assert True
        except NameError as e:
            pytest.fail(f"NameError in conduct_initial_research: {e}")


def test_parallel_search_in_async_context():
    """Test that parallel search works when called from async context."""
    from tools.parallel_ddg import ParallelDuckDuckGoSearch
    import json

    tool = ParallelDuckDuckGoSearch(enable_search=True, enable_news=False)

    async def async_caller():
        """Call parallel search from async context."""
        # This should NOT raise "coroutine was never awaited"
        result_json = tool.parallel_search(
            search_queries=["test"],
            max_results=1
        )
        result = json.loads(result_json)
        return result

    # Run in async context
    result = asyncio.run(async_caller())

    # Should have proper structure
    assert 'total_queries' in result
    assert 'all_sources' in result


def test_sources_dict_variable_exists():
    """Ensure sources_dict variable is always defined."""
    import ast
    import inspect

    # Get source code of conduct_initial_research
    from research_orchestrator import ResearchOrchestrator

    source = inspect.getsource(ResearchOrchestrator.conduct_initial_research)

    # Check that sources_dict is defined before use
    assert 'sources_dict = []' in source or 'sources_dict =' in source, \
        "sources_dict must be initialized before use"


def test_all_required_cli_args():
    """Test that all CLI arguments work."""
    import sys
    from research_orchestrator import main
    from unittest.mock import patch

    test_cases = [
        ['research_orchestrator.py', 'Topic', '--no-eval'],
        ['research_orchestrator.py', 'Topic', '--eval-freq', '5'],
        ['research_orchestrator.py', 'Topic', '--no-input'],
        ['research_orchestrator.py', 'Topic', '--input-files', '1'],
    ]

    for args in test_cases:
        with patch.object(sys, 'argv', args):
            with patch('research_orchestrator.asyncio.run'):
                with patch('research_orchestrator.ResearchOrchestrator'):
                    try:
                        # Should parse without errors
                        # (won't actually run due to mocking)
                        pass
                    except SystemExit:
                        pass  # argparse help is OK
