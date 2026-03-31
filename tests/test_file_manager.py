"""Unit tests for FileManager."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
from storage.file_manager import FileManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def file_manager(temp_dir):
    """Create FileManager instance."""
    return FileManager(base_dir=str(temp_dir))


def test_create_research_id(file_manager):
    """Test research ID generation."""
    research_id = file_manager.create_research_id()
    assert research_id.startswith("research-")
    assert len(research_id) > 15


def test_create_research_directory(file_manager):
    """Test research directory creation."""
    research_id = "research-test-123"
    research_dir = file_manager.create_research_directory(research_id)

    assert research_dir.exists()
    assert (research_dir / "rag").exists()
    assert (research_dir / "kb").exists()
    assert (research_dir / "memory").exists()
    assert (research_dir / "logs").exists()


@pytest.mark.asyncio
async def test_save_and_load_refinement(file_manager):
    """Test saving and loading refinements."""
    research_id = "research-test-123"
    file_manager.create_research_directory(research_id)

    content = "# Test Research\n\nThis is test content."

    # Save
    filepath = await file_manager.save_refinement(research_id, 1, content)
    assert filepath.exists()
    assert filepath.name == "refinement-0001.md"

    # Load
    loaded = await file_manager.load_refinement(research_id, 1)
    assert loaded == content


def test_get_latest_version(file_manager):
    """Test getting latest version number."""
    research_id = "research-test-123"
    file_manager.create_research_directory(research_id)

    # No refinements yet
    assert file_manager.get_latest_version(research_id) == 0

    # Create some refinements
    research_dir = file_manager.get_research_directory(research_id)
    (research_dir / "refinement-0001.md").touch()
    (research_dir / "refinement-0005.md").touch()
    (research_dir / "refinement-0003.md").touch()

    assert file_manager.get_latest_version(research_id) == 5


@pytest.mark.asyncio
async def test_save_and_load_metadata(file_manager):
    """Test metadata operations."""
    research_id = "research-test-123"
    file_manager.create_research_directory(research_id)

    metadata = {
        'research_id': research_id,
        'topic': 'Test Topic',
        'version': 1
    }

    # Save
    await file_manager.save_metadata(research_id, metadata)

    # Load
    loaded = await file_manager.load_metadata(research_id)
    assert loaded == metadata


def test_list_research_sessions(file_manager, temp_dir):
    """Test listing research sessions."""
    # Create some sessions
    (temp_dir / "research-001").mkdir()
    (temp_dir / "research-002").mkdir()
    (temp_dir / "not-research").mkdir()

    sessions = file_manager.list_research_sessions()

    assert len(sessions) == 2
    assert "research-001" in sessions
    assert "research-002" in sessions
    assert "not-research" not in sessions
