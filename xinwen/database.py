from __future__ import annotations
import sqlite3
import hashlib
from datetime import date, datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from config import DB_PATH


@dataclass
class Article:
    url: str
    title: str
    summary: str = ""
    source_name: str = ""
    source_category: str = ""
    publish_date: str = ""
    url_hash: str = ""
    title_hash: str = ""

    def __post_init__(self):
        if not self.url_hash:
            self.url_hash = hashlib.md5(self.url.encode()).hexdigest()
        if not self.title_hash:
            self.title_hash = hashlib.md5(self.title.strip().encode()).hexdigest()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            url_hash TEXT NOT NULL,
            title TEXT NOT NULL,
            title_hash TEXT NOT NULL,
            summary TEXT DEFAULT '',
            source_name TEXT DEFAULT '',
            source_category TEXT DEFAULT '',
            publish_date TEXT DEFAULT '',
            crawl_date TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(url_hash)
        );

        CREATE INDEX IF NOT EXISTS idx_articles_publish_date ON articles(publish_date);
        CREATE INDEX IF NOT EXISTS idx_articles_title_hash ON articles(title_hash);
        CREATE INDEX IF NOT EXISTS idx_articles_crawl_date ON articles(crawl_date);

        CREATE TABLE IF NOT EXISTS crawl_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            crawl_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            article_count INTEGER DEFAULT 0,
            error_message TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_crawl_logs_date ON crawl_logs(crawl_date);
    """)
    conn.commit()
    conn.close()


def insert_article(article: Article, crawl_date: str) -> bool:
    """Insert article, return True if inserted (not duplicate)."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM articles WHERE title_hash = ? AND publish_date = ?",
            (article.title_hash, article.publish_date),
        ).fetchone()
        if existing:
            conn.close()
            return False

        conn.execute(
            """INSERT OR IGNORE INTO articles
               (url, url_hash, title, title_hash, summary, source_name, source_category, publish_date, crawl_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                article.url,
                article.url_hash,
                article.title,
                article.title_hash,
                article.summary,
                article.source_name,
                article.source_category,
                article.publish_date,
                crawl_date,
            ),
        )
        conn.commit()
        inserted = conn.total_changes > 0
        return inserted
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_articles_by_date(target_date: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM articles WHERE publish_date = ? ORDER BY source_category, source_name, id",
        (target_date,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_crawl(source_name: str, crawl_date: str, status: str, article_count: int = 0, error_message: str = ""):
    conn = get_connection()
    conn.execute(
        """INSERT INTO crawl_logs (source_name, crawl_date, status, article_count, error_message)
           VALUES (?, ?, ?, ?, ?)""",
        (source_name, crawl_date, status, article_count, error_message),
    )
    conn.commit()
    conn.close()


def get_crawl_logs(crawl_date: Optional[str] = None) -> list[dict]:
    conn = get_connection()
    if crawl_date:
        rows = conn.execute(
            "SELECT * FROM crawl_logs WHERE crawl_date = ? ORDER BY id DESC", (crawl_date,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM crawl_logs ORDER BY id DESC LIMIT 100"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
