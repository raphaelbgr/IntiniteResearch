"""
Comprehensive system test - Run the actual code paths to find bugs.
No mocking - tests real code flow.
"""
import sys
import io
import asyncio
import tempfile
import shutil
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("COMPREHENSIVE SYSTEM TEST")
print("=" * 60)

def test_imports():
    """Test all imports work."""
    print("\n[1/10] Testing imports...")
    try:
        from utils.config_loader import load_config
        from utils.file_selector import FileSelector
        from utils.context_manager import ContextManager
        from utils.source_tracker import SourceTracker
        from storage.file_manager import FileManager
        from storage.vector_store import VectorStore
        from agents.research_agent import ResearchAgent
        from tools.parallel_ddg import ParallelDuckDuckGoSearch
        from refinement.refiner import RefinementEngine
        from refinement.evaluator import ResearchEvaluator
        from models.research_models import SearchSource
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_file_manager():
    """Test file manager."""
    print("\n[2/10] Testing FileManager...")
    try:
        from storage.file_manager import FileManager
        temp_dir = tempfile.mkdtemp()

        fm = FileManager(base_dir=temp_dir)
        research_id = fm.create_research_id()
        research_dir = fm.create_research_directory(research_id)

        assert research_dir.exists()
        assert (research_dir / "rag").exists()

        shutil.rmtree(temp_dir)
        print("✓ FileManager works")
        return True
    except Exception as e:
        print(f"✗ FileManager failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parallel_search():
    """Test parallel search tool."""
    print("\n[3/10] Testing ParallelDuckDuckGoSearch...")
    try:
        from tools.parallel_ddg import ParallelDuckDuckGoSearch
        import json

        tool = ParallelDuckDuckGoSearch(enable_search=True, enable_news=False)

        # Test validation
        result_json = tool.parallel_search(search_queries=[])
        result = json.loads(result_json)
        assert 'error' in result
        print("  ✓ Validation works")

        # Test too many
        result_json = tool.parallel_search(search_queries=["q" + str(i) for i in range(11)])
        result = json.loads(result_json)
        assert 'error' in result
        print("  ✓ Max limit enforcement works")

        print("✓ ParallelDuckDuckGoSearch works")
        return True
    except Exception as e:
        print(f"✗ ParallelDuckDuckGoSearch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_manager():
    """Test context manager."""
    print("\n[4/10] Testing ContextManager...")
    try:
        from utils.context_manager import ContextManager

        cm = ContextManager()

        # Test search term extraction
        content = "<!-- SEARCH_TERMS: term1, term2 -->\nContent"
        terms = cm.extract_search_terms(content)
        assert len(terms) == 2
        print("  ✓ Search term extraction works")

        # Test source extraction
        content = """<!--
SOURCES:
  SOURCE: Title | https://url.com
-->
Content"""
        sources = cm.extract_sources(content)
        assert len(sources) == 1
        print("  ✓ Source extraction works")

        # Test metadata formatting
        formatted = cm.format_refinement_with_metadata(
            content="Content",
            search_terms=["t1"],
            version=1,
            research_id="test",
            sources=[{"title": "T", "url": "https://u.com"}]
        )
        assert "<!-- RESEARCH_ID: test -->" in formatted
        print("  ✓ Metadata formatting works")

        print("✓ ContextManager works")
        return True
    except Exception as e:
        print(f"✗ ContextManager failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_source_tracker():
    """Test source tracker."""
    print("\n[5/10] Testing SourceTracker...")
    try:
        from utils.source_tracker import SourceTracker
        from models.research_models import SearchSource
        import json

        # Test extraction
        search_result = {
            "all_sources": [
                {"title": "Test", "url": "https://test.com", "snippet": "Snippet"}
            ]
        }
        sources = SourceTracker.extract_from_parallel_search(json.dumps(search_result))
        assert len(sources) == 1
        assert isinstance(sources[0], SearchSource)
        print("  ✓ Source extraction works")

        # Test conversion
        metadata = SourceTracker.sources_to_metadata_format(sources)
        assert len(metadata) == 1
        assert metadata[0]['title'] == "Test"
        print("  ✓ Metadata conversion works")

        print("✓ SourceTracker works")
        return True
    except Exception as e:
        print(f"✗ SourceTracker failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_research_agent_creation():
    """Test creating research agent."""
    print("\n[6/10] Testing ResearchAgent creation...")
    try:
        from agents.research_agent import ResearchAgent
        from pathlib import Path
        temp_dir = Path(tempfile.mkdtemp())

        config = {
            'base_url': 'http://localhost:1234/v1',
            'model': 'test-model',
            'api_key': 'test',
            'temperature': 0.7,
            'max_tokens': 2048
        }

        storage_config = {
            'memory_db': 'test.db'
        }

        agent = ResearchAgent(
            research_id="test-123",
            research_dir=temp_dir,
            lmstudio_config=config,
            storage_config=storage_config
        )

        assert agent.agent is not None
        print("  ✓ Agent created successfully")

        shutil.rmtree(temp_dir)
        print("✓ ResearchAgent works")
        return True
    except Exception as e:
        print(f"✗ ResearchAgent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_refinement_engine_creation():
    """Test creating refinement engine."""
    print("\n[7/10] Testing RefinementEngine creation...")
    try:
        from refinement.refiner import RefinementEngine
        from agents.research_agent import ResearchAgent
        from storage.file_manager import FileManager
        from storage.vector_store import VectorStore
        from pathlib import Path
        temp_dir = Path(tempfile.mkdtemp())

        # Create dependencies
        fm = FileManager(base_dir=str(temp_dir))
        research_id = fm.create_research_id()
        research_dir = fm.create_research_directory(research_id)

        config = {
            'base_url': 'http://localhost:1234/v1',
            'model': 'test',
            'api_key': 'test',
            'temperature': 0.7,
            'max_tokens': 2048
        }

        agent = ResearchAgent(
            research_id=research_id,
            research_dir=research_dir,
            lmstudio_config=config,
            storage_config={'memory_db': 'test.db'}
        )

        vs = VectorStore(research_id, research_dir, "sqlite")

        # Create refinement engine
        engine = RefinementEngine(
            research_id=research_id,
            research_agent=agent,
            file_manager=fm,
            vector_store=vs,
            refinement_delay=1,
            enable_evaluation=False
        )

        assert engine.research_id == research_id
        assert engine.refinement_delay == 1
        print("  ✓ RefinementEngine created")

        vs.close()
        shutil.rmtree(temp_dir)
        print("✓ RefinementEngine works")
        return True
    except Exception as e:
        print(f"✗ RefinementEngine failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluator_creation():
    """Test creating evaluator."""
    print("\n[8/10] Testing ResearchEvaluator creation...")
    try:
        from refinement.evaluator import ResearchEvaluator
        from agents.research_agent import ResearchAgent
        from storage.file_manager import FileManager
        from pathlib import Path
        temp_dir = Path(tempfile.mkdtemp())

        fm = FileManager(base_dir=str(temp_dir))
        research_id = fm.create_research_id()
        research_dir = fm.create_research_directory(research_id)

        config = {
            'base_url': 'http://localhost:1234/v1',
            'model': 'test',
            'api_key': 'test',
            'temperature': 0.7,
            'max_tokens': 2048
        }

        agent = ResearchAgent(
            research_id=research_id,
            research_dir=research_dir,
            lmstudio_config=config,
            storage_config={'memory_db': 'test.db'}
        )

        evaluator = ResearchEvaluator(
            research_id=research_id,
            research_agent=agent,
            file_manager=fm,
            research_dir=research_dir,
            base_topic="test topic",
            input_files_content="test input"
        )

        assert evaluator.research_id == research_id
        assert (research_dir / "report").exists()
        print("  ✓ ResearchEvaluator created")

        shutil.rmtree(temp_dir)
        print("✓ ResearchEvaluator works")
        return True
    except Exception as e:
        print(f"✗ ResearchEvaluator failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Test vector store."""
    print("\n[9/10] Testing VectorStore...")
    try:
        from storage.vector_store import VectorStore
        temp_dir = Path(tempfile.mkdtemp())

        vs = VectorStore("test", temp_dir, "sqlite")

        # Add chunks
        vs.add_document_chunks(1, ["Chunk 1", "Chunk 2"])

        # Search
        results = vs.search_similar("Chunk", limit=10)
        assert len(results) > 0
        print("  ✓ Vector operations work")

        vs.close()
        shutil.rmtree(temp_dir)
        print("✓ VectorStore works")
        return True
    except Exception as e:
        print(f"✗ VectorStore failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pydantic_models():
    """Test Pydantic models."""
    print("\n[10/10] Testing Pydantic models...")
    try:
        from models.research_models import SearchSource, SearchResults, RefinementMetadata

        # Test SearchSource
        source = SearchSource(title="Test", url="https://test.com")
        assert source.title == "Test"
        print("  ✓ SearchSource works")

        # Test SearchResults
        results = SearchResults(query="test", sources=[source], total_results=1)
        assert len(results.sources) == 1
        print("  ✓ SearchResults works")

        # Test RefinementMetadata
        metadata = RefinementMetadata(
            research_id="test",
            version=1,
            timestamp="2025-01-21T14:30:00"
        )
        assert metadata.version == 1
        print("  ✓ RefinementMetadata works")

        print("✓ Pydantic models work")
        return True
    except Exception as e:
        print(f"✗ Pydantic models failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    tests = [
        test_imports,
        test_file_manager,
        test_parallel_search,
        test_context_manager,
        test_source_tracker,
        test_research_agent_creation,
        test_refinement_engine_creation,
        test_evaluator_creation,
        test_vector_store,
        test_pydantic_models
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n✗ {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:40s} {status}")

    print("=" * 60)
    print(f"TOTAL: {passed}/{total} passed")

    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED! System is ready! ✓✓✓")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} TESTS FAILED ✗✗✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
