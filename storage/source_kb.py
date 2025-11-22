"""Source Knowledge Base for storing and querying discovered URLs/sources."""
from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()


class SourceKnowledgeBase:
    """Manages discovered sources/URLs with rich metadata for learning."""

    def __init__(self, research_id: str, base_dir: Path):
        """Initialize source knowledge base.

        Args:
            research_id: Unique research identifier
            base_dir: Base directory for storage
        """
        self.research_id = research_id
        self.base_dir = base_dir
        self.db_path = base_dir / "kb" / "sources.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for sources."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Main sources table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                research_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                snippet TEXT,
                domain TEXT,
                discovery_iteration INTEGER NOT NULL,
                search_term TEXT,
                relevance_score REAL DEFAULT 0.0,
                topic_tags TEXT,
                content_hash TEXT,
                is_useful INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(research_id, url)
            )
        """)

        # Search terms performance table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                research_id TEXT NOT NULL,
                term TEXT NOT NULL,
                iteration INTEGER NOT NULL,
                results_count INTEGER DEFAULT 0,
                score REAL DEFAULT 0.0,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for fast lookups
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sources_research
            ON sources(research_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sources_domain
            ON sources(research_id, domain)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sources_iteration
            ON sources(research_id, discovery_iteration)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_terms_research
            ON search_terms(research_id, iteration)
        """)

        self.conn.commit()
        logger.info(f"Initialized SourceKnowledgeBase at {self.db_path}")

    def add_sources(
        self,
        sources: List[Dict[str, Any]],
        iteration: int,
        search_term: Optional[str] = None
    ) -> int:
        """Add discovered sources to knowledge base.

        Args:
            sources: List of source dicts with url, title, snippet
            iteration: Which iteration discovered these
            search_term: Search term that found these sources

        Returns:
            Number of new sources added (excludes duplicates)
        """
        added = 0

        for source in sources:
            url = source.get('url', '').strip()
            if not url:
                continue

            title = source.get('title', '')
            snippet = source.get('snippet', source.get('body', ''))

            # Extract domain from URL
            domain = self._extract_domain(url)

            # Auto-detect language from search term
            language = self._detect_language(search_term) if search_term else 'en'

            # Generate simple relevance score based on content
            relevance = self._calculate_relevance(title, snippet)

            # Extract topic tags from title/snippet
            topic_tags = self._extract_topics(title, snippet)

            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO sources
                    (research_id, url, title, snippet, domain, discovery_iteration,
                     search_term, relevance_score, topic_tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.research_id,
                    url,
                    title,
                    snippet[:1000] if snippet else None,  # Limit snippet size
                    domain,
                    iteration,
                    search_term,
                    relevance,
                    json.dumps(topic_tags) if topic_tags else None
                ))

                if self.cursor.rowcount > 0:
                    added += 1

            except sqlite3.Error as e:
                logger.warning(f"Failed to add source {url}: {e}")

        self.conn.commit()

        if added > 0:
            logger.info(f"Added {added} new sources to KB (iteration {iteration})")

        return added

    def add_search_performance(
        self,
        performance_data: List[Dict[str, Any]],
        iteration: int
    ):
        """Store search term performance data.

        Args:
            performance_data: List of {term, results, score} dicts
            iteration: Which iteration these are from
        """
        for perf in performance_data:
            term = perf.get('term', '')
            results = perf.get('results', 0)
            score = perf.get('score', 0)
            language = self._detect_language(term)

            try:
                self.cursor.execute("""
                    INSERT INTO search_terms
                    (research_id, term, iteration, results_count, score, language)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.research_id,
                    term,
                    iteration,
                    results,
                    score,
                    language
                ))
            except sqlite3.Error as e:
                logger.warning(f"Failed to save search term {term}: {e}")

        self.conn.commit()

    def get_sources_count(self) -> int:
        """Get total number of unique sources.

        Returns:
            Count of sources in KB
        """
        self.cursor.execute("""
            SELECT COUNT(*) FROM sources WHERE research_id = ?
        """, (self.research_id,))
        return self.cursor.fetchone()[0]

    def get_sources_by_iteration(self, iteration: int) -> List[Dict[str, Any]]:
        """Get sources discovered in a specific iteration.

        Args:
            iteration: Iteration number

        Returns:
            List of source dictionaries
        """
        self.cursor.execute("""
            SELECT url, title, snippet, domain, search_term, relevance_score
            FROM sources
            WHERE research_id = ? AND discovery_iteration = ?
            ORDER BY relevance_score DESC
        """, (self.research_id, iteration))

        return [
            {
                'url': row[0],
                'title': row[1],
                'snippet': row[2],
                'domain': row[3],
                'search_term': row[4],
                'relevance_score': row[5]
            }
            for row in self.cursor.fetchall()
        ]

    def search_sources(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search sources by keyword.

        Args:
            query: Search query (searches title, snippet, domain)
            limit: Max results

        Returns:
            Matching sources
        """
        self.cursor.execute("""
            SELECT url, title, snippet, domain, discovery_iteration,
                   search_term, relevance_score
            FROM sources
            WHERE research_id = ?
            AND (title LIKE ? OR snippet LIKE ? OR domain LIKE ?)
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (
            self.research_id,
            f"%{query}%",
            f"%{query}%",
            f"%{query}%",
            limit
        ))

        return [
            {
                'url': row[0],
                'title': row[1],
                'snippet': row[2],
                'domain': row[3],
                'iteration': row[4],
                'search_term': row[5],
                'relevance_score': row[6]
            }
            for row in self.cursor.fetchall()
        ]

    def get_top_domains(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently found domains.

        Args:
            limit: Max domains to return

        Returns:
            List of {domain, count, avg_relevance}
        """
        self.cursor.execute("""
            SELECT domain, COUNT(*) as count, AVG(relevance_score) as avg_rel
            FROM sources
            WHERE research_id = ?
            GROUP BY domain
            ORDER BY count DESC
            LIMIT ?
        """, (self.research_id, limit))

        return [
            {
                'domain': row[0],
                'count': row[1],
                'avg_relevance': row[2]
            }
            for row in self.cursor.fetchall()
        ]

    def get_search_term_stats(self) -> Dict[str, Any]:
        """Get aggregated search term statistics.

        Returns:
            Stats about search performance across iterations
        """
        # Overall stats
        self.cursor.execute("""
            SELECT
                COUNT(*) as total_searches,
                AVG(score) as avg_score,
                SUM(results_count) as total_results
            FROM search_terms
            WHERE research_id = ?
        """, (self.research_id,))
        row = self.cursor.fetchone()

        # Best performing terms
        self.cursor.execute("""
            SELECT term, score, results_count
            FROM search_terms
            WHERE research_id = ?
            ORDER BY score DESC
            LIMIT 10
        """, (self.research_id,))
        best_terms = [
            {'term': r[0], 'score': r[1], 'results': r[2]}
            for r in self.cursor.fetchall()
        ]

        # Worst performing terms
        self.cursor.execute("""
            SELECT term, score, results_count
            FROM search_terms
            WHERE research_id = ?
            ORDER BY score ASC
            LIMIT 10
        """, (self.research_id,))
        worst_terms = [
            {'term': r[0], 'score': r[1], 'results': r[2]}
            for r in self.cursor.fetchall()
        ]

        # Language breakdown
        self.cursor.execute("""
            SELECT language, COUNT(*) as count, AVG(score) as avg_score
            FROM search_terms
            WHERE research_id = ?
            GROUP BY language
            ORDER BY avg_score DESC
        """, (self.research_id,))
        lang_stats = [
            {'language': r[0], 'count': r[1], 'avg_score': r[2]}
            for r in self.cursor.fetchall()
        ]

        return {
            'total_searches': row[0] or 0,
            'avg_score': row[1] or 0,
            'total_results': row[2] or 0,
            'best_terms': best_terms,
            'worst_terms': worst_terms,
            'language_performance': lang_stats
        }

    def get_kb_summary(self) -> str:
        """Generate a summary string for AI context.

        Returns:
            Formatted summary of KB contents
        """
        sources_count = self.get_sources_count()
        top_domains = self.get_top_domains(5)
        stats = self.get_search_term_stats()

        lines = [
            f"Knowledge Base Summary:",
            f"  Total Sources: {sources_count}",
            f"  Total Searches: {stats['total_searches']}",
            f"  Average Search Score: {stats['avg_score']:.1f}%",
        ]

        if top_domains:
            lines.append("  Top Domains:")
            for d in top_domains[:5]:
                lines.append(f"    - {d['domain']}: {d['count']} sources")

        if stats['best_terms']:
            lines.append("  Best Performing Terms:")
            for t in stats['best_terms'][:3]:
                lines.append(f"    - \"{t['term']}\": {t['score']:.0f}%")

        return "\n".join(lines)

    def is_url_known(self, url: str) -> bool:
        """Check if URL is already in knowledge base.

        Args:
            url: URL to check

        Returns:
            True if URL exists in KB
        """
        self.cursor.execute("""
            SELECT 1 FROM sources
            WHERE research_id = ? AND url = ?
            LIMIT 1
        """, (self.research_id, url))
        return self.cursor.fetchone() is not None

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return 'unknown'

    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character sets."""
        if not text:
            return 'en'

        # Check for non-ASCII character ranges
        has_cyrillic = any('\u0400' <= c <= '\u04FF' for c in text)
        has_chinese = any('\u4E00' <= c <= '\u9FFF' for c in text)
        has_japanese = any('\u3040' <= c <= '\u30FF' for c in text)
        has_korean = any('\uAC00' <= c <= '\uD7AF' for c in text)
        has_arabic = any('\u0600' <= c <= '\u06FF' for c in text)

        if has_cyrillic:
            return 'ru'
        elif has_chinese:
            return 'zh'
        elif has_japanese:
            return 'ja'
        elif has_korean:
            return 'ko'
        elif has_arabic:
            return 'ar'

        # Check for common language patterns
        text_lower = text.lower()
        if any(word in text_lower for word in ['como', 'para', 'guia', 'renda']):
            return 'pt'
        elif any(word in text_lower for word in ['cómo', 'guía', 'ingresos']):
            return 'es'
        elif any(word in text_lower for word in ['comment', 'revenu', 'guide']):
            return 'fr'
        elif any(word in text_lower for word in ['wie', 'anleitung', 'einkommen']):
            return 'de'

        return 'en'

    def _calculate_relevance(self, title: str, snippet: str) -> float:
        """Calculate simple relevance score (0-100)."""
        score = 50.0  # Base score

        # Boost for having both title and snippet
        if title and snippet:
            score += 10
        elif title:
            score += 5

        # Boost for longer content (more context)
        if snippet and len(snippet) > 200:
            score += 10
        if snippet and len(snippet) > 500:
            score += 10

        # Cap at 100
        return min(100.0, score)

    def _extract_topics(self, title: str, snippet: str) -> List[str]:
        """Extract simple topic tags from content."""
        text = f"{title or ''} {snippet or ''}".lower()
        topics = []

        # Simple keyword-based topic detection
        topic_keywords = {
            'trading': ['trading', 'trade', 'trader', 'exchange'],
            'automation': ['automat', 'bot', 'script', 'algorithm'],
            'investment': ['invest', 'portfolio', 'asset'],
            'security': ['secur', 'protect', 'safe', 'risk'],
            'beginner': ['beginner', 'start', 'basic', 'guide', 'intro'],
            'advanced': ['advanced', 'expert', 'professional', 'pro'],
            'news': ['news', 'update', 'latest', 'announce'],
            'tutorial': ['tutorial', 'how to', 'learn', 'course'],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)

        return topics[:5]  # Limit to 5 topics

    def close(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.debug("Closed SourceKnowledgeBase connection")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
