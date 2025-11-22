"""Interactive file selector for input folder."""
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from utils.logger import get_logger

logger = get_logger()
console = Console()


class FileSelector:
    """Interactive file selector for research inputs."""

    def __init__(self, input_dir: str = "./input"):
        """Initialize file selector.

        Args:
            input_dir: Directory containing input files
        """
        self.input_dir = Path(input_dir)
        self.input_dir.mkdir(parents=True, exist_ok=True)

    def list_input_files(self) -> List[Path]:
        """List all files in input directory.

        Returns:
            List of file paths
        """
        if not self.input_dir.exists():
            return []

        files = [
            f for f in self.input_dir.iterdir()
            if f.is_file() and not f.name.startswith('.')
        ]

        return sorted(files)

    def display_files(self, files: List[Path]):
        """Display files in a nice table.

        Args:
            files: List of file paths to display
        """
        if not files:
            console.print("[yellow]No files found in input directory[/yellow]")
            console.print(f"[dim]Place files in: {self.input_dir.absolute()}[/dim]")
            return

        table = Table(title="Available Input Files")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Filename", style="green")
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("Type", style="magenta")

        for i, file in enumerate(files, start=2):
            size = file.stat().st_size
            size_str = self._format_size(size)
            file_type = file.suffix.upper() or "FILE"

            table.add_row(
                str(i),
                file.name,
                size_str,
                file_type
            )

        console.print(table)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format.

        Args:
            size: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def select_files(self, auto_select: str = None) -> List[Path]:
        """Interactive file selection.

        Args:
            auto_select: Auto-select option ('0', '1', '2', '2,3', etc.) for non-interactive mode

        Returns:
            List of selected file paths
        """
        files = self.list_input_files()

        console.print("\n[bold cyan]═══ Input File Selection ═══[/bold cyan]\n")

        if not files:
            console.print("[yellow]No input files found.[/yellow]")
            console.print(f"[dim]Place files in: {self.input_dir.absolute()}[/dim]\n")
            return []

        self.display_files(files)

        console.print("\n[bold]Options:[/bold]")
        console.print("  [cyan]0[/cyan] - No input files (prompt only)")
        console.print("  [cyan]1[/cyan] - ALL files")
        console.print(f"  [cyan]2-{len(files)+1}[/cyan] - Specific file from list")
        console.print("  [cyan]2,3,4[/cyan] - Multiple files (comma-separated)")
        console.print()

        # Auto-select mode for non-interactive
        if auto_select is not None:
            choice = auto_select
            console.print(f"[dim]Auto-selected: {choice}[/dim]\n")
        else:
            while True:
                try:
                    choice = console.input("[bold green]Select files[/bold green] (default: 0): ").strip()
                    break
                except (EOFError, KeyboardInterrupt):
                    console.print("\n[dim]No input (using default: 0)[/dim]\n")
                    choice = "0"
                    break

        # Process selection
        while True:
            try:

                if not choice or choice == "0":
                    console.print("[dim]No input files selected[/dim]\n")
                    return []

                if choice == "1":
                    console.print(f"[green]Selected ALL {len(files)} files[/green]\n")
                    return files

                # Parse comma-separated choices
                if "," in choice:
                    indices = [int(x.strip()) - 2 for x in choice.split(",")]
                else:
                    indices = [int(choice) - 2]

                # Validate indices
                selected = []
                for idx in indices:
                    if 0 <= idx < len(files):
                        selected.append(files[idx])
                    else:
                        console.print(f"[red]Invalid choice: {idx + 2}[/red]")
                        raise ValueError()

                if selected:
                    console.print(f"[green]Selected {len(selected)} file(s):[/green]")
                    for f in selected:
                        console.print(f"  • {f.name}")
                    console.print()
                    return selected

            except (ValueError, IndexError):
                console.print("[red]Invalid input. Please try again.[/red]\n")
                continue

    def copy_files_to_session(
        self,
        files: List[Path],
        session_dir: Path
    ) -> List[Path]:
        """Copy selected files to research session.

        Args:
            files: Files to copy
            session_dir: Research session directory

        Returns:
            List of copied file paths in session
        """
        if not files:
            return []

        # Create input directory in session
        input_session_dir = session_dir / "input"
        input_session_dir.mkdir(parents=True, exist_ok=True)

        copied_files = []

        for file in files:
            dest = input_session_dir / file.name

            try:
                # Copy file
                import shutil
                shutil.copy2(file, dest)

                copied_files.append(dest)
                logger.info(f"Copied input file: {file.name}")

            except Exception as e:
                logger.error(f"Failed to copy {file.name}: {e}")

        return copied_files

    def read_input_files(self, files: List[Path]) -> str:
        """Read and format input files for AI context.

        Args:
            files: List of file paths to read

        Returns:
            Formatted string with file contents
        """
        if not files:
            return ""

        content_parts = [
            "# Input Files Provided by User\n",
            "*These files contain additional context for the research.*\n\n"
        ]

        for file in files:
            try:
                content_parts.append(f"## File: {file.name}\n\n")

                # Check if text file
                if file.suffix.lower() in ['.txt', '.md', '.json', '.csv', '.xml', '.html']:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        content_parts.append(f"```\n{file_content}\n```\n\n")
                else:
                    # Binary or unknown file
                    content_parts.append(
                        f"*Binary file: {file.suffix or 'unknown type'}*\n\n"
                    )

            except Exception as e:
                logger.error(f"Failed to read {file.name}: {e}")
                content_parts.append(f"*Error reading file: {e}*\n\n")

        return "".join(content_parts)
