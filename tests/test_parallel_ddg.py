"""Unit tests for ParallelDuckDuckGoSearch tool."""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from tools.parallel_ddg import ParallelDuckDuckGoSearch


@pytest.fixture
def search_tool():
    """Create search tool instance."""
    return ParallelDuckDuckGoSearch(
        enable_search=True,
        enable_news=False,
        fixed_max_results=3
    )


def test_tool_initialization(search_tool):
    """Test tool initialization."""
    assert search_tool.name == "parallel_duckduckgo"
    assert search_tool.fixed_max_results == 3
    assert search_tool.timeout == 10


def test_parallel_search_validation_empty_list(search_tool):
    """Test validation with empty list."""
    result_json = search_tool.parallel_search(search_queries=[])
    result = json.loads(result_json)

    assert 'error' in result
    assert "At least 1 search query required" in result['error']


def test_parallel_search_validation_too_many(search_tool):
    """Test validation with too many queries."""
    queries = [f"query{i}" for i in range(11)]  # 11 queries
    result_json = search_tool.parallel_search(search_queries=queries)
    result = json.loads(result_json)

    assert 'error' in result
    assert "Maximum 10 parallel searches" in result['error']


def test_parallel_search_validation_not_list(search_tool):
    """Test validation with non-list input."""
    result_json = search_tool.parallel_search(search_queries="not a list")
    result = json.loads(result_json)

    assert 'error' in result
    assert "must be a list" in result['error']


@patch('tools.parallel_ddg.DDGS')
def test_parallel_search_success(mock_ddgs, search_tool):
    """Test successful parallel search."""
    # Mock DDGS response
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = [
        {"title": "Result 1", "href": "https://example1.com", "body": "Content 1"},
        {"title": "Result 2", "href": "https://example2.com", "body": "Content 2"}
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance
    mock_ddgs.return_value.__exit__.return_value = None

    result_json = search_tool.parallel_search(
        search_queries=["test query"],
        max_results=2
    )
    result = json.loads(result_json)

    assert result['total_queries'] == 1
    assert result['successful_queries'] == 1
    assert result['total_results'] == 2
    assert len(result['all_sources']) == 2
    assert result['all_sources'][0]['title'] == "Result 1"
    assert result['all_sources'][0]['url'] == "https://example1.com"


@patch('tools.parallel_ddg.DDGS')
def test_parallel_news_success(mock_ddgs):
    """Test successful parallel news search."""
    tool = ParallelDuckDuckGoSearch(enable_search=False, enable_news=True)

    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.news.return_value = [
        {"title": "News 1", "url": "https://news1.com", "body": "News content"}
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance
    mock_ddgs.return_value.__exit__.return_value = None

    result_json = tool.parallel_news(search_queries=["test news"])
    result = json.loads(result_json)

    assert result['total_queries'] == 1
    assert len(result['all_sources']) == 1


@patch('tools.parallel_ddg.DDGS')
def test_source_deduplication(mock_ddgs, search_tool):
    """Test that duplicate sources are removed."""
    mock_ddgs_instance = MagicMock()
    # Same URL in multiple results
    mock_ddgs_instance.text.return_value = [
        {"title": "Result", "href": "https://example.com", "body": "Content"}
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance
    mock_ddgs.return_value.__exit__.return_value = None

    result_json = search_tool.parallel_search(
        search_queries=["query1", "query2"]  # Two queries with same result
    )
    result = json.loads(result_json)

    # Should deduplicate
    urls = [s['url'] for s in result['all_sources']]
    assert len(urls) == len(set(urls))  # All unique


def test_tool_has_correct_methods(search_tool):
    """Test tool has registered methods."""
    assert hasattr(search_tool, 'parallel_search')
    assert callable(search_tool.parallel_search)


def test_news_tool_has_correct_methods():
    """Test news tool has correct methods."""
    tool = ParallelDuckDuckGoSearch(enable_search=False, enable_news=True)
    assert hasattr(tool, 'parallel_news')
    assert callable(tool.parallel_news)
