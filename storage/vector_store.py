"""Vector database management for RAG."""
from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlite3
from utils.logger import get_logger

logger = get_logger()


class VectorStore:
    """Manages vector embeddings for RAG."""

    def __init__(
        self,
        research_id: str,
        base_dir: Path,
        db_type: str = "sqlite"
    ):
        """Initialize vector store.

        Args:
            research_id: Unique research identifier
            base_dir: Base directory for storage
            db_type: Type of vector database ('sqlite' or 'pgvector')
        """
        self.research_id = research_id
        self.base_dir = base_dir
        self.db_type = db_type
        self.db_path = base_dir / "rag" / "vectors.db"

        if db_type == "sqlite":
            self._init_sqlite()
        elif db_type == "pgvector":
            self._init_pgvector()
        else:
            raise ValueError(f"Unsupported db_type: {db_type}")

    def _init_sqlite(self):
        """Initialize SQLite vector database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create connection
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Create table for document chunks
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                research_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for faster lookups
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_research_version
            ON document_chunks(research_id, version)
        """)

        self.conn.commit()
        logger.info(f"Initialized SQLite vector store at {self.db_path}")

    def _init_pgvector(self):
        """Initialize PgVector database."""
        # TODO: Implement PgVector initialization
        # This would require pgvector extension and psycopg2
        raise NotImplementedError("PgVector support coming soon")

    def add_document_chunks(
        self,
        version: int,
        chunks: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add document chunks to vector store.

        Args:
            version: Refinement version number
            chunks: List of text chunks
            embeddings: Optional list of embedding vectors
            metadata: Optional metadata dictionary
        """
        if self.db_type == "sqlite":
            import json

            for i, chunk in enumerate(chunks):
                embedding_blob = None
                if embeddings and i < len(embeddings):
                    # Convert embedding to bytes for storage
                    import struct
                    embedding_blob = struct.pack(
                        f'{len(embeddings[i])}f',
                        *embeddings[i]
                    )

                metadata_json = json.dumps(metadata) if metadata else None

                self.cursor.execute("""
                    INSERT INTO document_chunks
                    (research_id, version, chunk_index, content, embedding, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.research_id,
                    version,
                    i,
                    chunk,
                    embedding_blob,
                    metadata_json
                ))

            self.conn.commit()
            logger.info(
                f"Added {len(chunks)} chunks for version {version} "
                f"to vector store"
            )

    def search_similar(
        self,
        query: str,
        limit: int = 10,
        version: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks.

        Note: This is a simple keyword search. For true semantic search,
        you would need to:
        1. Generate query embedding
        2. Compute cosine similarity with stored embeddings
        3. Return top-k results

        Args:
            query: Search query
            limit: Maximum number of results
            version: Optional version to filter by

        Returns:
            List of matching chunks with metadata
        """
        if self.db_type == "sqlite":
            # Simple keyword search (for demonstration)
            # In production, use proper vector similarity search
            query_sql = """
                SELECT
                    version,
                    chunk_index,
                    content,
                    metadata,
                    created_at
                FROM document_chunks
                WHERE research_id = ?
                AND content LIKE ?
            """

            params = [self.research_id, f"%{query}%"]

            if version is not None:
                query_sql += " AND version = ?"
                params.append(version)

            query_sql += " ORDER BY version DESC, chunk_index ASC LIMIT ?"
            params.append(limit)

            self.cursor.execute(query_sql, params)

            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'version': row[0],
                    'chunk_index': row[1],
                    'content': row[2],
                    'metadata': row[3],
                    'created_at': row[4]
                })

            return results

        return []

    def get_all_chunks(
        self,
        version: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all chunks for this research.

        Args:
            version: Optional version to filter by

        Returns:
            List of all chunks
        """
        if self.db_type == "sqlite":
            query_sql = """
                SELECT
                    version,
                    chunk_index,
                    content,
                    metadata,
                    created_at
                FROM document_chunks
                WHERE research_id = ?
            """

            params = [self.research_id]

            if version is not None:
                query_sql += " AND version = ?"
                params.append(version)

            query_sql += " ORDER BY version DESC, chunk_index ASC"

            self.cursor.execute(query_sql, params)

            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'version': row[0],
                    'chunk_index': row[1],
                    'content': row[2],
                    'metadata': row[3],
                    'created_at': row[4]
                })

            return results

        return []

    def close(self):
        """Close database connection."""
        if self.db_type == "sqlite" and hasattr(self, 'conn'):
            self.conn.close()
            logger.debug("Closed vector store connection")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
