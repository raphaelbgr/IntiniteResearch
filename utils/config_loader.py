"""Configuration loader utility."""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_lmstudio_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract LMStudio configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        LMStudio configuration
    """
    return config.get('lmstudio', {})


def get_research_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract research configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Research configuration
    """
    return config.get('research', {})


def get_vector_db_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract vector database configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Vector database configuration
    """
    return config.get('vector_db', {})


def get_storage_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract storage configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Storage configuration
    """
    return config.get('storage', {})
