"""File system management for research outputs."""
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json
import aiofiles
import asyncio
from utils.logger import get_logger

logger = get_logger()


class FileManager:
    """Manages research file system structure."""

    def __init__(self, base_dir: str = "./generation"):
        """Initialize file manager.

        Args:
            base_dir: Base directory for all research outputs
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_research_id(self) -> str:
        """Generate unique research ID based on timestamp.

        Returns:
            Research ID string (e.g., 'research-20250121-143022')
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"research-{timestamp}"

    def create_research_directory(self, research_id: str) -> Path:
        """Create directory structure for a research session.

        Args:
            research_id: Unique research identifier

        Returns:
            Path to research directory
        """
        research_dir = self.base_dir / research_id
        research_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (research_dir / "rag").mkdir(exist_ok=True)
        (research_dir / "kb").mkdir(exist_ok=True)
        (research_dir / "memory").mkdir(exist_ok=True)
        (research_dir / "logs").mkdir(exist_ok=True)
        (research_dir / "conclusion").mkdir(exist_ok=True)
        (research_dir / "agent-conclusions").mkdir(exist_ok=True)
        (research_dir / "bmad-sessions").mkdir(exist_ok=True)

        logger.info(f"Created research directory: {research_dir}")

        return research_dir

    def get_research_directory(self, research_id: str) -> Path:
        """Get path to research directory.

        Args:
            research_id: Unique research identifier

        Returns:
            Path to research directory
        """
        return self.base_dir / research_id

    async def save_refinement(
        self,
        research_id: str,
        version: int,
        content: str
    ) -> Path:
        """Save a refinement version to file.

        Args:
            research_id: Unique research identifier
            version: Refinement version number
            content: Document content

        Returns:
            Path to saved file
        """
        research_dir = self.get_research_directory(research_id)
        filename = f"refinement-{version:04d}.md"
        filepath = research_dir / filename

        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)

        logger.info(f"Saved {filename} ({len(content)} chars)")

        return filepath

    async def load_refinement(
        self,
        research_id: str,
        version: int
    ) -> Optional[str]:
        """Load a refinement version from file.

        Args:
            research_id: Unique research identifier
            version: Refinement version number

        Returns:
            Document content or None if not found
        """
        research_dir = self.get_research_directory(research_id)
        filename = f"refinement-{version:04d}.md"
        filepath = research_dir / filename

        if not filepath.exists():
            return None

        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()

        return content

    def get_latest_version(self, research_id: str) -> int:
        """Get the latest refinement version number.

        Args:
            research_id: Unique research identifier

        Returns:
            Latest version number (0 if none exist)
        """
        research_dir = self.get_research_directory(research_id)

        if not research_dir.exists():
            return 0

        refinements = list(research_dir.glob("refinement-*.md"))

        if not refinements:
            return 0

        versions = []
        for ref in refinements:
            try:
                # Extract version number from filename
                version_str = ref.stem.split('-')[1]
                versions.append(int(version_str))
            except (IndexError, ValueError):
                continue

        return max(versions) if versions else 0

    async def save_metadata(
        self,
        research_id: str,
        metadata: dict
    ) -> Path:
        """Save research metadata.

        Args:
            research_id: Unique research identifier
            metadata: Metadata dictionary

        Returns:
            Path to metadata file
        """
        research_dir = self.get_research_directory(research_id)
        metadata_path = research_dir / "kb" / "metadata.json"

        async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(metadata, indent=2))

        logger.debug(f"Saved metadata for {research_id}")

        return metadata_path

    async def load_metadata(self, research_id: str) -> Optional[dict]:
        """Load research metadata.

        Args:
            research_id: Unique research identifier

        Returns:
            Metadata dictionary or None if not found
        """
        research_dir = self.get_research_directory(research_id)
        metadata_path = research_dir / "kb" / "metadata.json"

        if not metadata_path.exists():
            return None

        async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)

    def list_research_sessions(self) -> List[str]:
        """List all research session IDs.

        Returns:
            List of research IDs
        """
        if not self.base_dir.exists():
            return []

        sessions = [
            d.name for d in self.base_dir.iterdir()
            if d.is_dir() and d.name.startswith("research-")
        ]

        return sorted(sessions, reverse=True)  # Most recent first

    def get_research_sessions_with_details(self) -> List[dict]:
        """Get all research sessions with their details.

        Returns:
            List of dicts with research_id, topic, latest_version, started_at, status
        """
        sessions = []
        session_ids = self.list_research_sessions()

        for research_id in session_ids:
            research_dir = self.get_research_directory(research_id)
            metadata_path = research_dir / "kb" / "metadata.json"

            # Get latest version
            latest_version = self.get_latest_version(research_id)

            # Load metadata if exists
            topic = "Unknown topic"
            started_at = None
            ended_at = None
            total_sources = 0

            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        topic = metadata.get('topic', 'Unknown topic')
                        started_at = metadata.get('started_at')
                        ended_at = metadata.get('ended_at')
                        total_sources = metadata.get('total_sources', 0)
                except (json.JSONDecodeError, IOError):
                    pass

            # Determine status
            if ended_at:
                status = "completed"
            elif latest_version > 0:
                status = "in_progress"
            else:
                status = "initialized"

            sessions.append({
                'research_id': research_id,
                'topic': topic,
                'latest_version': latest_version,
                'started_at': started_at,
                'ended_at': ended_at,
                'total_sources': total_sources,
                'status': status
            })

        return sessions
