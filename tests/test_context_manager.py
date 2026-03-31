"""Unit tests for ContextManager."""
import pytest
from utils.context_manager import ContextManager


@pytest.fixture
def context_manager():
    """Create ContextManager instance."""
    return ContextManager()


def test_extract_search_terms(context_manager):
    """Test extracting search terms from content."""
    content = """<!-- SEARCH_TERMS: quantum computing, AI research, machine learning -->

# Research Document
"""
    terms = context_manager.extract_search_terms(content)
    assert len(terms) == 3
    assert "quantum computing" in terms
    assert "AI research" in terms


def test_extract_sources(context_manager):
    """Test extracting sources from content."""
    content = """<!--
SOURCES:
  SOURCE: Python.org | https://python.org
  SOURCE: Wikipedia | https://wikipedia.org
-->

# Content
"""
    sources = context_manager.extract_sources(content)
    assert len(sources) == 2
    assert sources[0]['title'] == "Python.org"
    assert sources[0]['url'] == "https://python.org"


def test_format_refinement_with_metadata(context_manager):
    """Test formatting refinement with metadata."""
    content = "# Research\n\nContent here."
    search_terms = ["term1", "term2"]
    sources = [{"title": "Source", "url": "https://example.com"}]

    formatted = context_manager.format_refinement_with_metadata(
        content=content,
        search_terms=search_terms,
        version=3,
        research_id="test-123",
        sources=sources
    )

    assert "<!-- RESEARCH_ID: test-123 -->" in formatted
    assert "<!-- VERSION: 0003 -->" in formatted
    assert "<!-- SEARCH_TERMS: term1, term2 -->" in formatted
    assert "SOURCE: Source | https://example.com" in formatted
    assert content in formatted


def test_generate_search_variations_first_iteration(context_manager):
    """Test search variation generation for first iteration."""
    variations = context_manager.generate_search_variations(
        base_topic="quantum computing",
        previous_searches=[],
        iteration=1
    )

    assert len(variations) >= 5
    assert any("overview" in v.lower() or "basics" in v.lower() for v in variations)
    assert any("quantum computing" in v.lower() for v in variations)


def test_generate_search_variations_later_iterations(context_manager):
    """Test search variation generation for later iterations."""
    previous = ["quantum basics", "quantum algorithms"]

    variations = context_manager.generate_search_variations(
        base_topic="quantum computing",
        previous_searches=previous,
        iteration=5
    )

    assert len(variations) > 0
    # Should have variations based on previous
    assert any("detailed" in v.lower() or "recent" in v.lower() for v in variations)


def test_extract_research_gaps(context_manager):
    """Test gap extraction from refinements."""
    refinements = [
        {
            'content': """# Section
TODO: Add examples

## Short Section
Brief text.
"""
        }
    ]

    gaps = context_manager.extract_research_gaps(refinements)

    assert len(gaps) > 0
    assert any("Add examples" in gap for gap in gaps)


def test_build_context_prompt(context_manager):
    """Test building context prompt."""
    base_prompt = "Refine this document."
    previous_refinements = [
        {
            'version': 1,
            'content': "# Research v1",
            'search_terms': ["term1", "term2"]
        }
    ]
    input_files = "# Input File\n\nUser notes."

    prompt = context_manager.build_context_prompt(
        base_prompt=base_prompt,
        previous_refinements=previous_refinements,
        input_files_content=input_files
    )

    assert "Input File" in prompt
    assert "Research v1" in prompt
    assert "Refine this document" in prompt
    assert "term1" in prompt or "term2" in prompt
