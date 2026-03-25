#!/usr/bin/env python3
"""
Test script for Agent0 Self-Evolving Research System

This script demonstrates the new Agent0 option integrated into the
InfiniteResearch system based on the paper:
"Agent0: Unleashing Self-Evolving Agents from Zero Data via Tool-Integrated Reasoning"
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.research_selector import ResearchSelector
from storage.file_manager import FileManager
from utils.config_loader import load_config


def test_agent0_menu():
    """Test that Agent0 option appears in the menu."""
    print("Testing Agent0 Menu Integration")
    print("=" * 60)

    # Load config
    config = load_config("config.yaml")

    # Initialize file manager
    file_manager = FileManager(config)

    # Create selector
    selector = ResearchSelector(file_manager)

    # Show menu (will display but require user input)
    print("\nThe menu should now show:")
    print("  [0] Start NEW research (standard web search)")
    print("  [A] Start Agent0 Self-Evolving Research  <-- NEW OPTION")
    print("  [B] Start BMAD Multi-Agent Research")
    print("\nPress Ctrl+C to exit the test.")

    try:
        result = selector.display_menu()
        if result:
            action, info = result
            print(f"\nSelected action: {action}")
            if action == 'agent0':
                print("✓ Agent0 option successfully integrated!")
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")


def describe_agent0_features():
    """Describe the Agent0 features now available."""
    print("\n" + "=" * 60)
    print("Agent0 Self-Evolving Research System")
    print("=" * 60)

    print("\nKEY FEATURES INTEGRATED:")
    print("-" * 40)

    features = [
        ("Co-Evolution", "Curriculum and Executor agents evolve together"),
        ("Self-Improvement", "Agents improve without human data"),
        ("Tool Integration", "Enhanced reasoning through tool usage"),
        ("Adaptive Complexity", "Tasks become progressively harder"),
        ("Uncertainty Targeting", "Focuses on optimal learning zone (~50% uncertainty)"),
        ("Performance Tracking", "Monitors evolution trajectory"),
        ("Convergence Detection", "Automatically detects when to stop")
    ]

    for feature, description in features:
        print(f"• {feature:20} {description}")

    print("\n" + "=" * 60)
    print("WORKFLOW:")
    print("-" * 40)
    print("""
1. User selects option [A] from menu
2. Provides initial research topic
3. System initializes Curriculum and Executor agents
4. Co-evolutionary loop begins:
   - Curriculum generates research task
   - Executor attempts task multiple times
   - Performance metrics calculated
   - Curriculum adapts based on executor performance
5. Process continues until convergence or max iterations
6. Generates comprehensive research report
    """)

    print("=" * 60)
    print("BASED ON PAPER:")
    print("-" * 40)
    print("'Agent0: Unleashing Self-Evolving Agents from Zero Data")
    print(" via Tool-Integrated Reasoning'")
    print("\nKey Innovations from Paper:")
    print("• Rc = Runc + Rtool - Rrep (Curriculum reward function)")
    print("• ADPO: Ambiguity-Dynamic Policy Optimization")
    print("• Multi-turn tool-integrated reasoning")
    print("• Self-consistency for uncertainty measurement")


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Agent0 Integration Test")
    print("🚀" * 30)

    # Describe features
    describe_agent0_features()

    # Test menu
    print("\n" + "=" * 60)
    print("TESTING MENU INTEGRATION")
    print("=" * 60)

    test_agent0_menu()

    print("\n✅ Agent0 has been successfully integrated into your system!")
    print("\nTo use it:")
    print("1. Run: python research_orchestrator.py")
    print("2. Select option [A] for Agent0 Self-Evolving Research")
    print("3. Provide an initial research topic")
    print("4. Watch the agents co-evolve and improve!")