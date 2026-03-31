"""Beautiful CLI logger using Rich for amazing terminal output."""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich import box
from rich.text import Text

# NOTE: UTF-8 encoding is configured in research_orchestrator.py (entry point)


class BeautifulLogger:
    """Beautiful CLI logger with Rich formatting."""

    def __init__(
        self,
        name: str = "InfiniteResearch",
        level: str = "INFO",
        log_file: Optional[str] = None
    ):
        """Initialize beautiful logger.

        Args:
            name: Logger name
            level: Logging level
            log_file: Optional log file path
        """
        # Create console with explicit UTF-8 support for multilingual output
        self.console = Console(force_terminal=True, color_system="auto")
        self.name = name

        # Setup logging with Rich
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(message)s",
            handlers=[
                RichHandler(
                    rich_tracebacks=True,
                    markup=True,
                    show_time=True,
                    show_path=False,
                    console=self.console
                )
            ]
        )

        self.logger = logging.getLogger(name)

        # Add file handler if specified (with UTF-8 encoding for multilingual support)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def header(self, text: str, style: str = "bold cyan"):
        """Print beautiful header."""
        self.console.print()
        self.console.rule(f"[{style}]{text}[/{style}]", style=style)
        self.console.print()

    def section(self, title: str, content: str = "", style: str = "cyan"):
        """Print section with title."""
        panel = Panel(
            content if content else "",
            title=f"[{style}]{title}[/{style}]",
            border_style=style,
            box=box.ROUNDED
        )
        self.console.print(panel)

    def banner(self, lines: list, style: str = "bold green"):
        """Print beautiful banner."""
        self.console.print()
        width = max(len(line) for line in lines) + 4
        border = "═" * width

        self.console.print(f"[{style}]╔{border}╗[/{style}]")
        for line in lines:
            padding = width - len(line) - 2
            self.console.print(
                f"[{style}]║[/{style}] {line}{' ' * padding} [{style}]║[/{style}]"
            )
        self.console.print(f"[{style}]╚{border}╝[/{style}]")
        self.console.print()

    def info(self, message: str, exc_info: bool = False):
        """Log info message."""
        self.logger.info(message, exc_info=exc_info)

    def success(self, message: str):
        """Log success message."""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def warning(self, message: str, exc_info: bool = False):
        """Log warning message."""
        self.logger.warning(f"[yellow]⚠[/yellow] {message}", exc_info=exc_info)

    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(f"[bold red]✗[/bold red] {message}", exc_info=exc_info)

    def debug(self, message: str, exc_info: bool = False):
        """Log debug message."""
        self.logger.debug(f"[dim]{message}[/dim]", exc_info=exc_info)

    def step(self, step_num: int, total_steps: int, description: str):
        """Log a step in a process."""
        self.console.print(
            f"[bold cyan]Step {step_num}/{total_steps}:[/bold cyan] {description}"
        )

    def research_status(
        self,
        research_id: str,
        version: int,
        search_terms: list,
        sources_count: int
    ):
        """Display research status beautifully."""
        table = Table(
            title="Research Status",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
            box=box.ROUNDED
        )

        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Research ID", research_id)
        table.add_row("Version", f"{version:04d}")
        table.add_row("Search Terms", str(len(search_terms)))
        table.add_row("Sources Found", str(sources_count))

        self.console.print(table)

    def search_progress(self, queries: list):
        """Show search progress."""
        table = Table(
            title="Parallel Search Execution",
            show_header=True,
            header_style="bold green",
            border_style="green",
            box=box.SIMPLE
        )

        table.add_column("#", style="dim", width=4)
        table.add_column("Query", style="cyan")
        table.add_column("Status", style="green", width=10)

        for i, query in enumerate(queries, 1):
            table.add_row(str(i), query, "Searching...")

        self.console.print(table)

    def search_results(self, total_queries: int, total_results: int, sources: int):
        """Display search results summary."""
        panel = Panel(
            f"[bold white]Queries Executed:[/bold white] {total_queries}\n"
            f"[bold white]Total Results:[/bold white] {total_results}\n"
            f"[bold white]Unique Sources:[/bold white] {sources}",
            title="[bold green]Search Complete[/bold green]",
            border_style="green",
            box=box.DOUBLE
        )
        self.console.print(panel)

    def refinement_iteration(
        self,
        current_version: int,
        new_version: int,
        search_terms: list,
        gaps: list,
        char_count: int
    ):
        """Display refinement iteration info."""
        self.console.print()
        self.console.rule(
            f"[bold yellow]Refinement {current_version} → {new_version}[/bold yellow]",
            style="yellow"
        )

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="cyan bold", width=18)
        table.add_column(style="white")

        table.add_row("Search Terms:", f"{len(search_terms)} queries")
        if gaps:
            table.add_row("Gaps Identified:", f"{len(gaps)} areas")
        table.add_row("Document Size:", f"{char_count:,} characters")

        self.console.print(table)
        self.console.print()

    def sources_table(self, sources: list, max_display: int = 10):
        """Display sources in a beautiful table."""
        if not sources:
            return

        table = Table(
            title=f"Sources Consulted ({len(sources)} total)",
            show_header=True,
            header_style="bold magenta",
            border_style="magenta",
            box=box.ROUNDED
        )

        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="cyan", max_width=40)
        table.add_column("URL", style="blue", max_width=50, overflow="fold")

        for i, source in enumerate(sources[:max_display], 1):
            title = source.get('title', 'Unknown')[:40]
            url = source.get('url', '')[:50]
            table.add_row(str(i), title, url)

        if len(sources) > max_display:
            table.add_row(
                "...",
                f"[dim]and {len(sources) - max_display} more[/dim]",
                ""
            )

        self.console.print(table)

    def progress_bar(self, description: str = "Processing"):
        """Create a progress bar context manager."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )

    def countdown(self, seconds: int, message: str = "Waiting"):
        """Show countdown timer."""
        import time

        with self.progress_bar() as progress:
            task = progress.add_task(
                f"[cyan]{message}...",
                total=seconds
            )

            for i in range(seconds):
                time.sleep(1)
                progress.update(task, advance=1)

    def final_summary(
        self,
        research_id: str,
        total_versions: int,
        total_sources: int,
        research_dir: str
    ):
        """Display final research summary."""
        self.console.print()
        panel = Panel(
            f"[bold white]Research ID:[/bold white] [cyan]{research_id}[/cyan]\n"
            f"[bold white]Total Refinements:[/bold white] [green]{total_versions}[/green]\n"
            f"[bold white]Sources Consulted:[/bold white] [magenta]{total_sources}[/magenta]\n"
            f"[bold white]Output Directory:[/bold white] [blue]{research_dir}[/blue]",
            title="[bold green]✓ Research Session Complete[/bold green]",
            border_style="green",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    def input_prompt(self, prompt: str, default: str = "") -> str:
        """Beautiful input prompt."""
        return self.console.input(f"[bold cyan]❯[/bold cyan] {prompt}: ")

    def list_item(self, text: str, style: str = "white"):
        """Print a list item."""
        self.console.print(f"  [bold cyan]•[/bold cyan] [{style}]{text}[/{style}]")

    def separator(self):
        """Print a separator line."""
        self.console.print("[dim]" + "─" * 60 + "[/dim]")

    def phase_start(self, phase_num: int, phase_name: str):
        """Mark the start of a phase."""
        self.console.print()
        self.console.rule(
            f"[bold green]Phase {phase_num}: {phase_name}[/bold green]",
            style="green"
        )
        self.console.print()

    def model_info(self, model_name: str, base_url: str):
        """Display model information."""
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column(style="cyan bold", width=15)
        table.add_column(style="white")

        table.add_row("LLM Model:", model_name)
        table.add_row("Server:", base_url)

        self.console.print(table)
