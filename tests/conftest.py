"""Pytest configuration and shared fixtures."""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def mock_lmstudio_config():
    """Mock LMStudio configuration."""
    return {
        'base_url': 'http://localhost:1234/v1',
        'model': 'test-model',
        'api_key': 'lm-studio',
        'temperature': 0.7,
        'max_tokens': 2048
    }


@pytest.fixture
def mock_research_config():
    """Mock research configuration."""
    return {
        'parallel_search_enabled': True,
        'refinement_delay': 10,
        'output_dir': './generation',
        'enable_evaluation': True,
        'evaluation_frequency': 10
    }


@pytest.fixture
def mock_storage_config():
    """Mock storage configuration."""
    return {
        'type': 'sqlite',
        'memory_db': 'agent_memory.db',
        'knowledge_db': 'knowledge.db'
    }


@pytest.fixture
def mock_vector_db_config():
    """Mock vector DB configuration."""
    return {
        'type': 'sqlite',
        'chunk_size': 512,
        'chunk_overlap': 50
    }
