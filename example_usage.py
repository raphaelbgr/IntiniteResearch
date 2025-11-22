"""
Example usage of Infinite Research components.

This demonstrates how to use the system programmatically
instead of via the command-line interface.
"""

import asyncio
from pathlib import Path
from utils.config_loader import load_config
from storage.file_manager import FileManager
from storage.vector_store import VectorStore
from agents.research_agent import ResearchAgent
from agents.worker_pool import WorkerPool
from refinement.refiner import RefinementEngine
from utils.logger import setup_logger


async def example_basic_research():
    """Example: Basic research without refinement."""
    print("=" * 70)
    print("Example 1: Basic Research")
    print("=" * 70)

    # Load config
    config = load_config()

    # Setup logger
    logger = setup_logger(level="INFO")

    # Initialize file manager
    fm = FileManager(base_dir="./generation")

    # Create research session
    research_id = fm.create_research_id()
    research_dir = fm.create_research_directory(research_id)

    logger.info(f"Research ID: {research_id}")

    # Initialize agent
    agent = ResearchAgent(
        research_id=research_id,
        research_dir=research_dir,
        lmstudio_config=config['lmstudio'],
        storage_config=config['storage']
    )

    # Conduct research
    topic = "What is quantum entanglement?"
    result = await agent.research(topic)

    # Save result
    await fm.save_refinement(research_id, version=1, content=result)

    logger.info(f"Research saved to: {research_dir / 'refinement-0001.md'}")
    print(f"\nResult preview:\n{result[:500]}...\n")


async def example_parallel_research():
    """Example: Parallel research with workers."""
    print("=" * 70)
    print("Example 2: Parallel Research with Workers")
    print("=" * 70)

    # Load config
    config = load_config()

    # Setup logger
    logger = setup_logger(level="INFO")

    # Initialize components
    fm = FileManager(base_dir="./generation")
    research_id = fm.create_research_id()
    research_dir = fm.create_research_directory(research_id)

    logger.info(f"Research ID: {research_id}")

    # Initialize worker pool with 3 workers
    worker_pool = WorkerPool(
        num_workers=3,
        lmstudio_config=config['lmstudio'],
        research_dir=research_dir
    )

    # Conduct parallel research
    topic = "The history of artificial intelligence"
    results = await worker_pool.research_parallel(topic)

    # Aggregate results
    aggregated = worker_pool.aggregate_results(results)

    # Save result
    await fm.save_refinement(research_id, version=1, content=aggregated)

    logger.info(f"Parallel research completed")
    logger.info(f"Workers used: {len(results)}")
    logger.info(f"Total length: {len(aggregated)} characters")


async def example_single_refinement():
    """Example: Load and refine a document once."""
    print("=" * 70)
    print("Example 3: Single Refinement")
    print("=" * 70)

    # Load config
    config = load_config()

    # Setup logger
    logger = setup_logger(level="INFO")

    # List existing research sessions
    fm = FileManager(base_dir="./generation")
    sessions = fm.list_research_sessions()

    if not sessions:
        logger.warning("No existing research sessions found!")
        logger.info("Run example_basic_research() first")
        return

    # Use most recent session
    research_id = sessions[0]
    research_dir = fm.get_research_directory(research_id)

    logger.info(f"Using research session: {research_id}")

    # Check latest version
    latest_version = fm.get_latest_version(research_id)
    logger.info(f"Latest version: {latest_version}")

    if latest_version == 0:
        logger.warning("No documents found in this session!")
        return

    # Initialize components
    vector_store = VectorStore(
        research_id=research_id,
        base_dir=research_dir,
        db_type=config['vector_db']['type']
    )

    agent = ResearchAgent(
        research_id=research_id,
        research_dir=research_dir,
        lmstudio_config=config['lmstudio'],
        storage_config=config['storage']
    )

    refiner = RefinementEngine(
        research_id=research_id,
        research_agent=agent,
        file_manager=fm,
        vector_store=vector_store,
        refinement_delay=5
    )

    # Execute single refinement
    new_version = await refiner.refine_once(latest_version)

    logger.info(f"Refinement complete: version {latest_version} -> {new_version}")
    logger.info(f"New document: {research_dir / f'refinement-{new_version:04d}.md'}")

    # Cleanup
    vector_store.close()


async def example_limited_refinements():
    """Example: Run refinements with a limit."""
    print("=" * 70)
    print("Example 4: Limited Refinements (3 iterations)")
    print("=" * 70)

    # Load config
    config = load_config()

    # Setup logger
    logger = setup_logger(level="INFO")

    # Initialize components
    fm = FileManager(base_dir="./generation")
    research_id = fm.create_research_id()
    research_dir = fm.create_research_directory(research_id)

    # Create initial document
    agent = ResearchAgent(
        research_id=research_id,
        research_dir=research_dir,
        lmstudio_config=config['lmstudio'],
        storage_config=config['storage']
    )

    # Quick research
    topic = "What is machine learning?"
    result = await agent.research(topic)
    await fm.save_refinement(research_id, version=1, content=result)

    # Initialize refiner
    vector_store = VectorStore(
        research_id=research_id,
        base_dir=research_dir,
        db_type=config['vector_db']['type']
    )

    refiner = RefinementEngine(
        research_id=research_id,
        research_agent=agent,
        file_manager=fm,
        vector_store=vector_store,
        refinement_delay=5
    )

    # Run 3 refinements
    current_version = 1
    max_refinements = 3

    for i in range(max_refinements):
        logger.info(f"Refinement {i+1}/{max_refinements}")
        current_version = await refiner.refine_once(current_version)
        await asyncio.sleep(2)  # Brief pause

    logger.info(f"Completed {max_refinements} refinements")
    logger.info(f"Final version: {current_version}")
    logger.info(f"Documents in: {research_dir}")

    # Cleanup
    vector_store.close()


async def example_vector_search():
    """Example: Search vector database."""
    print("=" * 70)
    print("Example 5: Vector Database Search")
    print("=" * 70)

    # Setup logger
    logger = setup_logger(level="INFO")

    # List existing research sessions
    fm = FileManager(base_dir="./generation")
    sessions = fm.list_research_sessions()

    if not sessions:
        logger.warning("No existing research sessions found!")
        return

    # Use most recent session
    research_id = sessions[0]
    research_dir = fm.get_research_directory(research_id)

    logger.info(f"Searching in: {research_id}")

    # Open vector store
    vector_store = VectorStore(
        research_id=research_id,
        base_dir=research_dir,
        db_type="sqlite"
    )

    # Search for content
    query = "artificial intelligence"
    results = vector_store.search_similar(query, limit=5)

    logger.info(f"Found {len(results)} results for '{query}'")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. Version {result['version']}, Chunk {result['chunk_index']}")
        print(f"   {result['content'][:200]}...")

    # Cleanup
    vector_store.close()


def main():
    """Run examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Infinite Research - Examples" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    examples = [
        ("Basic Research", example_basic_research),
        ("Parallel Research", example_parallel_research),
        ("Single Refinement", example_single_refinement),
        ("Limited Refinements", example_limited_refinements),
        ("Vector Search", example_vector_search),
    ]

    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  {len(examples) + 1}. Run all examples")
    print("  0. Exit")

    try:
        choice = int(input("\nSelect example (0-{}): ".format(len(examples) + 1)))

        if choice == 0:
            print("Exiting...")
            return

        if choice == len(examples) + 1:
            # Run all
            for name, func in examples:
                print(f"\n\nRunning: {name}\n")
                asyncio.run(func())
                print("\n" + "-" * 70)
        elif 1 <= choice <= len(examples):
            # Run selected
            name, func = examples[choice - 1]
            print(f"\nRunning: {name}\n")
            asyncio.run(func())
        else:
            print("Invalid choice!")

    except ValueError:
        print("Invalid input!")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
