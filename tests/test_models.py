"""Unit tests for Pydantic models."""
import pytest
from pydantic import ValidationError
from models.research_models import SearchSource, SearchResults, RefinementMetadata, ResearchOutput


def test_search_source_valid():
    """Test valid SearchSource creation."""
    source = SearchSource(
        title="Python.org",
        url="https://python.org",
        snippet="Official Python documentation"
    )

    assert source.title == "Python.org"
    assert source.url == "https://python.org"
    assert source.snippet == "Official Python documentation"


def test_search_source_without_snippet():
    """Test SearchSource without snippet."""
    source = SearchSource(
        title="Test",
        url="https://test.com"
    )

    assert source.title == "Test"
    assert source.url == "https://test.com"
    assert source.snippet is None


def test_search_source_missing_required():
    """Test SearchSource with missing required fields."""
    with pytest.raises(ValidationError):
        SearchSource(title="Test")  # Missing url


def test_search_results_valid():
    """Test valid SearchResults."""
    results = SearchResults(
        query="test query",
        sources=[
            SearchSource(title="S1", url="https://s1.com"),
            SearchSource(title="S2", url="https://s2.com")
        ],
        total_results=2
    )

    assert results.query == "test query"
    assert len(results.sources) == 2
    assert results.total_results == 2


def test_search_results_defaults():
    """Test SearchResults default values."""
    results = SearchResults(query="test")

    assert results.sources == []
    assert results.total_results == 0


def test_refinement_metadata_valid():
    """Test valid RefinementMetadata."""
    metadata = RefinementMetadata(
        research_id="research-123",
        version=5,
        search_terms=["term1", "term2"],
        sources=[SearchSource(title="S", url="https://s.com")],
        timestamp="2025-01-21T14:30:00"
    )

    assert metadata.research_id == "research-123"
    assert metadata.version == 5
    assert len(metadata.search_terms) == 2
    assert len(metadata.sources) == 1


def test_refinement_metadata_defaults():
    """Test RefinementMetadata default values."""
    metadata = RefinementMetadata(
        research_id="test",
        version=1,
        timestamp="2025-01-21T14:30:00"
    )

    assert metadata.search_terms == []
    assert metadata.sources == []


def test_research_output_valid():
    """Test valid ResearchOutput."""
    output = ResearchOutput(
        content="# Research\n\nContent here.",
        sources_used=[SearchSource(title="S", url="https://s.com")],
        key_findings=["Finding 1", "Finding 2"],
        gaps_identified=["Gap 1"]
    )

    assert "Research" in output.content
    assert len(output.sources_used) == 1
    assert len(output.key_findings) == 2
    assert len(output.gaps_identified) == 1


def test_research_output_minimal():
    """Test ResearchOutput with minimal required fields."""
    output = ResearchOutput(content="Content")

    assert output.content == "Content"
    assert output.sources_used == []
    assert output.key_findings is None
    assert output.gaps_identified is None
