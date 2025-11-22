"""Test script to verify installation and imports."""
import sys
import io

# Fix Windows encoding for Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")

    try:
        import agno
        print(f"✓ agno ({agno.__version__ if hasattr(agno, '__version__') else 'installed'})")
    except ImportError as e:
        print(f"✗ agno - {e}")
        return False

    try:
        import openai
        print(f"✓ openai ({openai.__version__})")
    except ImportError as e:
        print(f"✗ openai - {e}")
        return False

    try:
        from ddgs import DDGS
        print(f"✓ ddgs (DuckDuckGo search)")
    except ImportError as e:
        print(f"✗ ddgs - {e}")
        return False

    try:
        import pydantic
        print(f"✓ pydantic ({pydantic.__version__})")
    except ImportError as e:
        print(f"✗ pydantic - {e}")
        return False

    try:
        import yaml
        print(f"✓ pyyaml")
    except ImportError as e:
        print(f"✗ pyyaml - {e}")
        return False

    try:
        import aiofiles
        print(f"✓ aiofiles")
    except ImportError as e:
        print(f"✗ aiofiles - {e}")
        return False

    try:
        from rich.console import Console
        print(f"✓ rich")
    except ImportError as e:
        print(f"✗ rich - {e}")
        return False

    return True

def test_project_imports():
    """Test that our project modules can be imported."""
    print("\nTesting project imports...")

    try:
        from utils.config_loader import load_config
        print("✓ utils.config_loader")
    except ImportError as e:
        print(f"✗ utils.config_loader - {e}")
        return False

    try:
        from utils.logger import setup_logger
        print("✓ utils.logger")
    except ImportError as e:
        print(f"✗ utils.logger - {e}")
        return False

    try:
        from utils.file_selector import FileSelector
        print("✓ utils.file_selector")
    except ImportError as e:
        print(f"✗ utils.file_selector - {e}")
        return False

    try:
        from utils.context_manager import ContextManager
        print("✓ utils.context_manager")
    except ImportError as e:
        print(f"✗ utils.context_manager - {e}")
        return False

    try:
        from storage.file_manager import FileManager
        print("✓ storage.file_manager")
    except ImportError as e:
        print(f"✗ storage.file_manager - {e}")
        return False

    try:
        from storage.vector_store import VectorStore
        print("✓ storage.vector_store")
    except ImportError as e:
        print(f"✗ storage.vector_store - {e}")
        return False

    try:
        from agents.research_agent import ResearchAgent
        print("✓ agents.research_agent")
    except ImportError as e:
        print(f"✗ agents.research_agent - {e}")
        return False

    try:
        from tools.parallel_ddg import ParallelDuckDuckGoSearch
        print("✓ tools.parallel_ddg")
    except ImportError as e:
        print(f"✗ tools.parallel_ddg - {e}")
        return False

    try:
        from refinement.refiner import RefinementEngine
        print("✓ refinement.refiner")
    except ImportError as e:
        print(f"✗ refinement.refiner - {e}")
        return False

    try:
        from models.research_models import SearchSource
        print("✓ models.research_models")
    except ImportError as e:
        print(f"✗ models.research_models - {e}")
        return False

    return True

def test_config():
    """Test that config.yaml exists and is valid."""
    print("\nTesting configuration...")

    try:
        from utils.config_loader import load_config
        config = load_config()

        if 'lmstudio' in config:
            print(f"✓ LMStudio config found")
            print(f"  - Base URL: {config['lmstudio'].get('base_url')}")
            print(f"  - Model: {config['lmstudio'].get('model')}")
        else:
            print("✗ LMStudio config missing")
            return False

        if 'research' in config:
            print(f"✓ Research config found")
        else:
            print("✗ Research config missing")
            return False

        return True
    except Exception as e:
        print(f"✗ Config error - {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Infinite Research - Setup Test")
    print("=" * 60)

    results = []

    # Test dependencies
    results.append(("Dependencies", test_imports()))

    # Test project imports
    results.append(("Project Imports", test_project_imports()))

    # Test config
    results.append(("Configuration", test_config()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Ensure LMStudio is running with a model loaded")
        print("2. Run: python test_parallel_search.py")
        print("3. Run: python research_orchestrator.py \"Test topic\"")
        return 0
    else:
        print("\n✗ Some tests failed. Please install missing dependencies:")
        print("pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
