"""Interactive research session selector."""
from typing import Optional, Tuple
from datetime import datetime
from storage.file_manager import FileManager


class ResearchSelector:
    """Interactive selector for research sessions."""

    def __init__(self, file_manager: FileManager):
        """Initialize selector.

        Args:
            file_manager: FileManager instance
        """
        self.file_manager = file_manager

    def display_menu(self) -> Optional[Tuple[str, dict]]:
        """Display interactive menu for research selection.

        Returns:
            Tuple of (action, session_info) where:
            - action is 'new', 'continue', or 'compile'
            - session_info is None for new, or dict with session details
        """
        sessions = self.file_manager.get_research_sessions_with_details()

        # Filter to show only sessions that can be continued (have at least 1 version)
        continuable = [s for s in sessions if s['latest_version'] > 0]

        print("\n" + "=" * 70)
        print("  INFINITE RESEARCH REFINEMENT SYSTEM")
        print("=" * 70)
        print("\nSelect an option:\n")

        # Option 0: New research
        print("  [0] Start NEW research")
        print()

        if continuable:
            print("  --- Existing Research ---\n")

            for i, session in enumerate(continuable, 1):
                self._display_session_option(i, session)

            print()
            print("  --- Actions ---")
            print(f"  [C] Compile/Generate CONCLUSION for a research")
            print()

        print("=" * 70)

        # Get user input
        while True:
            try:
                choice = input("\nEnter choice (0=new, 1-N=continue, C=compile): ").strip()

                if choice == '0' or choice.lower() == 'new':
                    return ('new', None)

                if choice.lower() == 'c':
                    # Compile mode - ask which research
                    return self._select_for_compile(continuable)

                choice_num = int(choice)

                if 1 <= choice_num <= len(continuable):
                    selected = continuable[choice_num - 1]
                    print(f"\n>>> Continuing research: {selected['topic'][:60]}...")
                    return ('continue', selected)
                else:
                    print(f"Invalid choice. Enter 0-{len(continuable)} or C")

            except ValueError:
                print("Please enter a valid number or C")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                return None

    def _select_for_compile(self, sessions: list) -> Optional[Tuple[str, dict]]:
        """Select a research session for compilation.

        Args:
            sessions: List of available sessions

        Returns:
            Tuple of ('compile', session_info) or None
        """
        if not sessions:
            print("No research sessions available to compile.")
            return None

        print("\n" + "-" * 50)
        print("SELECT RESEARCH TO COMPILE")
        print("-" * 50)

        for i, session in enumerate(sessions, 1):
            topic = session['topic'][:50] + "..." if len(session['topic']) > 50 else session['topic']
            print(f"  [{i}] {topic}")
            print(f"      v{session['latest_version']} | {session['total_sources']} sources")

        print(f"  [0] Cancel")

        while True:
            try:
                choice = input("\nSelect research to compile: ").strip()

                if choice == '0':
                    return self.display_menu()  # Go back to main menu

                choice_num = int(choice)
                if 1 <= choice_num <= len(sessions):
                    selected = sessions[choice_num - 1]
                    print(f"\n>>> Compiling: {selected['topic'][:50]}...")
                    return ('compile', selected)
                else:
                    print(f"Invalid. Enter 0-{len(sessions)}")

            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                return None

    def _display_session_option(self, number: int, session: dict):
        """Display a single session option.

        Args:
            number: Option number
            session: Session details dict
        """
        topic = session['topic']
        # Truncate topic for display
        if len(topic) > 50:
            topic = topic[:47] + "..."

        version = session['latest_version']
        status = session['status']
        sources = session.get('total_sources', 0)

        # Format started date
        started = ""
        if session.get('started_at'):
            try:
                dt = datetime.fromisoformat(session['started_at'])
                started = dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                started = session['started_at'][:16]

        # Status indicator
        if status == 'completed':
            status_icon = "[DONE]"
        elif status == 'in_progress':
            status_icon = "[...]"
        else:
            status_icon = "[NEW]"

        print(f"  [{number}] {status_icon} {topic}")
        print(f"      Version: {version} | Sources: {sources} | Started: {started}")
        print(f"      ID: {session['research_id']}")
        print()

    def select_or_new(self, auto_continue: Optional[str] = None) -> Optional[Tuple[str, dict]]:
        """Select research or start new, with optional auto-selection.

        Args:
            auto_continue: If provided, auto-select this research_id or 'latest'

        Returns:
            Tuple of (action, session_info)
        """
        if auto_continue:
            sessions = self.file_manager.get_research_sessions_with_details()
            continuable = [s for s in sessions if s['latest_version'] > 0]

            if auto_continue.lower() == 'latest' and continuable:
                # Auto-continue latest
                selected = continuable[0]
                print(f"\n>>> Auto-continuing latest research: {selected['topic'][:50]}...")
                return ('continue', selected)

            # Try to find by research_id
            for session in continuable:
                if session['research_id'] == auto_continue:
                    print(f"\n>>> Auto-continuing research: {session['topic'][:50]}...")
                    return ('continue', session)

            print(f"Warning: Research '{auto_continue}' not found. Starting interactive menu.")

        return self.display_menu()
