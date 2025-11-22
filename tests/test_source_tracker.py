"""Unit tests for SourceTracker."""
import pytest
import json
from utils.source_tracker import SourceTracker
from models.research_models import SearchSource


def test_extract_from_parallel_search():
    """Test extracting sources from parallel search JSON."""
    search_result = {
        "all_sources": [
            {"title": "Python.org", "url": "https://python.org", "snippet": "Official Python"},
            {"title": "Wikipedia", "url": "https://wikipedia.org", "snippet": "Encyclopedia"}
        ]
    }

    result_json = json.dumps(search_result)
    sources = SourceTracker.extract_from_parallel_search(result_json)

    assert len(sources) == 2
    assert isinstance(sources[0], SearchSource)
    assert sources[0].title == "Python.org"
    assert sources[0].url == "https://python.org"


def test_extract_from_queries_format():
    """Test extracting from queries array format."""
    search_result = {
        "queries": [
            {
                "status": "success",
                "results": [
                    {"title": "Source 1", "href": "https://example.com/1", "body": "Description 1"},
                    {"title": "Source 2", "href": "https://example.com/2", "body": "Description 2"}
                ]
            }
        ]
    }

    result_json = json.dumps(search_result)
    sources = SourceTracker.extract_from_parallel_search(result_json)

    assert len(sources) == 2
    assert sources[0].url == "https://example.com/1"


def test_sources_to_metadata_format():
    """Test converting SearchSource to dict format."""
    sources = [
        SearchSource(title="Test", url="https://test.com", snippet="Snippet"),
        SearchSource(title="Test2", url="https://test2.com")
    ]

    metadata = SourceTracker.sources_to_metadata_format(sources)

    assert len(metadata) == 2
    assert metadata[0] == {"title": "Test", "url": "https://test.com"}
    assert metadata[1] == {"title": "Test2", "url": "https://test2.com"}


def test_format_sources_for_display():
    """Test formatting sources for display."""
    sources = [
        SearchSource(title=f"Source {i}", url=f"https://example{i}.com")
        for i in range(5)
    ]

    formatted = SourceTracker.format_sources_for_display(sources, max_display=3)

    assert "## Sources" in formatted
    assert "Source 0" in formatted
    assert "Source 2" in formatted
    assert "and 2 more sources" in formatted


def test_get_unique_domains():
    """Test extracting unique domains."""
    sources = [
        SearchSource(title="S1", url="https://python.org/docs"),
        SearchSource(title="S2", url="https://python.org/tutorial"),
        SearchSource(title="S3", url="https://wikipedia.org/wiki"),
    ]

    domains = SourceTracker.get_unique_domains(sources)

    assert len(domains) == 2
    assert "python.org" in domains
    assert "wikipedia.org" in domains


def test_empty_sources():
    """Test handling empty sources."""
    result_json = json.dumps({"all_sources": []})
    sources = SourceTracker.extract_from_parallel_search(result_json)
    assert len(sources) == 0


def test_invalid_json():
    """Test handling invalid JSON."""
    sources = SourceTracker.extract_from_parallel_search("invalid json")
    assert len(sources) == 0


def test_deduplication():
    """Test source deduplication by URL."""
    search_result = {
        "all_sources": [
            {"title": "Python", "url": "https://python.org", "snippet": "1"},
            {"title": "Python Duplicate", "url": "https://python.org", "snippet": "2"},
            {"title": "Wikipedia", "url": "https://wikipedia.org", "snippet": "3"}
        ]
    }

    result_json = json.dumps(search_result)
    sources = SourceTracker.extract_from_parallel_search(result_json)

    # Should deduplicate by URL
    assert len(sources) == 2
    urls = [s.url for s in sources]
    assert len(urls) == len(set(urls))
