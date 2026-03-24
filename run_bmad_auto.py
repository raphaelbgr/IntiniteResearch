"""
BMAD Auto Mode Runner

This script runs the BMAD orchestrator in fully automated mode.
The BMadOperator (AI agent) will make ALL decisions automatically.

NO user input is required - it's 100% autonomous!
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.bmad_orchestrator import BMadTeamsSession


def main():
    """Run BMAD in fully automated mode."""
    
    # LMStudio config
    lmstudio_config = {
        'model': 'local-model',
        'base_url': 'http://localhost:1234/v1',
        'api_key': 'lm-studio',
        'temperature': 0.7,
        'max_tokens': 4096
    }

    # Define your research goal here
    goal = """
    I want to build a software that can literally do crypto operations.
    Help me design the architecture, choose the right technologies, 
    identify security considerations, and create a roadmap for development.
    """

    # Create session
    session = BMadTeamsSession(
        research_id="bmad-auto-001",
        research_dir=Path("./generation/bmad-auto-test"),
        lmstudio_config=lmstudio_config
    )

    # Run in AUTO MODE - completely autonomous!
    print("\n" + "="*70)
    print("  BMAD AUTO MODE - 100% AUTONOMOUS")
    print("="*70)
    print("\nThe Operator AI will run the entire session automatically.")
    print("You can sit back and watch, or press Ctrl+C to interrupt.\n")
    
    session.run_auto_mode(goal=goal.strip())


if __name__ == "__main__":
    main()
