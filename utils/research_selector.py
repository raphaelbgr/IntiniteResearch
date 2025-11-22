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
            - action is 'new' or 'continue'
            - session_info is None for new, or dict with session details for continue
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
            print("  --- Continue Existing Research ---\n")

            for i, session in enumerate(continuable, 1):
                self._display_session_option(i, session)

            print()

        print("=" * 70)

        # Get user input
        while True:
            try:
                choice = input("\nEnter your choice (0 for new, or number to continue): ").strip()

                if choice == '0' or choice.lower() == 'new':
                    return ('new', None)

                choice_num = int(choice)

                if 1 <= choice_num <= len(continuable):
                    selected = continuable[choice_num - 1]
                    print(f"\n>>> Continuing research: {selected['topic'][:60]}...")
                    return ('continue', selected)
                else:
                    print(f"Invalid choice. Enter 0-{len(continuable)}")

            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nExiting...")
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
