"""Pydantic models for structured research data."""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SearchSource(BaseModel):
    """A single search result source."""

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Quantum Computing Basics",
            "url": "https://example.com/quantum",
            "snippet": "Introduction to quantum computing..."
        }
    })

    title: str = Field(..., description="Title of the source")
    url: str = Field(..., description="URL of the source")
    snippet: Optional[str] = Field(None, description="Short snippet/description")


class SearchResults(BaseModel):
    """Aggregated search results with sources."""

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "query": "quantum computing",
            "sources": [
                {"title": "IBM Quantum", "url": "https://ibm.com/quantum", "snippet": "..."}
            ],
            "total_results": 5
        }
    })

    query: str = Field(..., description="The search query")
    sources: List[SearchSource] = Field(default_factory=list, description="List of sources found")
    total_results: int = Field(0, description="Total number of results")


class RefinementMetadata(BaseModel):
    """Metadata for a refinement version."""

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "research_id": "research-20250121-143022",
            "version": 3,
            "search_terms": ["quantum hardware", "quantum algorithms"],
            "sources": [],
            "timestamp": "2025-01-21T14:30:22"
        }
    })

    research_id: str = Field(..., description="Unique research session ID")
    version: int = Field(..., description="Refinement version number")
    search_terms: List[str] = Field(default_factory=list, description="Search terms used")
    sources: List[SearchSource] = Field(default_factory=list, description="Sources consulted")
    timestamp: str = Field(..., description="ISO timestamp of creation")


class ResearchOutput(BaseModel):
    """Structured research document output."""

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "content": "# Research Document\n\n...",
            "sources_used": [],
            "key_findings": ["Finding 1", "Finding 2"],
            "gaps_identified": ["Gap 1"]
        }
    })

    content: str = Field(..., description="Main research content in markdown")
    sources_used: List[SearchSource] = Field(default_factory=list, description="Sources cited")
    key_findings: Optional[List[str]] = Field(None, description="Key findings summary")
    gaps_identified: Optional[List[str]] = Field(None, description="Research gaps found")
