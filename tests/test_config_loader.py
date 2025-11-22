"""Unit tests for config_loader."""
import pytest
import tempfile
import yaml
from pathlib import Path
from utils.config_loader import (
    load_config,
    get_lmstudio_config,
    get_research_config,
    get_vector_db_config,
    get_storage_config
)


@pytest.fixture
def temp_config():
    """Create temporary config file."""
    config_data = {
        'lmstudio': {
            'base_url': 'http://localhost:1234/v1',
            'model': 'test-model',
            'temperature': 0.7
        },
        'research': {
            'parallel_search_enabled': True,
            'refinement_delay': 10,
            'enable_evaluation': True,
            'evaluation_frequency': 10
        },
        'vector_db': {
            'type': 'sqlite',
            'chunk_size': 512
        },
        'storage': {
            'type': 'sqlite',
            'memory_db': 'test.db'
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink()


def test_load_config(temp_config):
    """Test loading config file."""
    config = load_config(temp_config)

    assert 'lmstudio' in config
    assert 'research' in config
    assert 'vector_db' in config
    assert 'storage' in config


def test_load_config_missing_file():
    """Test loading non-existent config file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_get_lmstudio_config(temp_config):
    """Test extracting LMStudio config."""
    config = load_config(temp_config)
    lmstudio = get_lmstudio_config(config)

    assert lmstudio['base_url'] == 'http://localhost:1234/v1'
    assert lmstudio['model'] == 'test-model'
    assert lmstudio['temperature'] == 0.7


def test_get_research_config(temp_config):
    """Test extracting research config."""
    config = load_config(temp_config)
    research = get_research_config(config)

    assert research['parallel_search_enabled'] is True
    assert research['refinement_delay'] == 10
    assert research['enable_evaluation'] is True


def test_get_vector_db_config(temp_config):
    """Test extracting vector DB config."""
    config = load_config(temp_config)
    vector_db = get_vector_db_config(config)

    assert vector_db['type'] == 'sqlite'
    assert vector_db['chunk_size'] == 512


def test_get_storage_config(temp_config):
    """Test extracting storage config."""
    config = load_config(temp_config)
    storage = get_storage_config(config)

    assert storage['type'] == 'sqlite'
    assert storage['memory_db'] == 'test.db'


def test_missing_sections():
    """Test handling missing config sections."""
    empty_config = {}

    assert get_lmstudio_config(empty_config) == {}
    assert get_research_config(empty_config) == {}
    assert get_vector_db_config(empty_config) == {}
    assert get_storage_config(empty_config) == {}
