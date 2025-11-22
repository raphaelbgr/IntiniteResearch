"""Unit tests for VectorStore."""
import pytest
from pathlib import Path
import tempfile
import shutil
from storage.vector_store import VectorStore


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def vector_store(temp_dir):
    """Create VectorStore instance."""
    vs = VectorStore(
        research_id="test-123",
        base_dir=temp_dir,
        db_type="sqlite"
    )
    yield vs
    # Close connection after test
    vs.close()


def test_initialization(vector_store, temp_dir):
    """Test vector store initialization."""
    assert vector_store.research_id == "test-123"
    assert vector_store.db_path.exists()
    assert (temp_dir / "rag" / "vectors.db").exists()


def test_add_document_chunks(vector_store):
    """Test adding document chunks."""
    chunks = ["Chunk 1 content", "Chunk 2 content", "Chunk 3 content"]

    vector_store.add_document_chunks(
        version=1,
        chunks=chunks,
        embeddings=None,
        metadata={'test': 'value'}
    )

    # Query to verify
    all_chunks = vector_store.get_all_chunks(version=1)
    assert len(all_chunks) == 3
    assert all_chunks[0]['content'] == "Chunk 1 content"


def test_search_similar(vector_store):
    """Test searching similar chunks."""
    chunks = [
        "Quantum computing basics",
        "Machine learning fundamentals",
        "Quantum algorithms NISQ"
    ]

    vector_store.add_document_chunks(version=1, chunks=chunks)

    # Search for quantum
    results = vector_store.search_similar("quantum", limit=10)

    assert len(results) > 0
    # Should find chunks with "quantum" in them
    assert any("quantum" in r['content'].lower() for r in results)


def test_get_all_chunks(vector_store):
    """Test getting all chunks."""
    vector_store.add_document_chunks(version=1, chunks=["V1 chunk"])
    vector_store.add_document_chunks(version=2, chunks=["V2 chunk"])

    # Get all chunks
    all_chunks = vector_store.get_all_chunks()
    assert len(all_chunks) == 2

    # Get version-specific
    v1_chunks = vector_store.get_all_chunks(version=1)
    assert len(v1_chunks) == 1
    assert v1_chunks[0]['content'] == "V1 chunk"


def test_context_manager(temp_dir):
    """Test context manager usage."""
    with VectorStore("test", temp_dir, "sqlite") as vs:
        vs.add_document_chunks(version=1, chunks=["Test"])
        assert len(vs.get_all_chunks()) == 1

    # Should close automatically


def test_invalid_db_type():
    """Test invalid database type."""
    with pytest.raises(ValueError):
        VectorStore("test", Path("/tmp"), "invalid_type")
