import sqlite3
import os
from typing import List, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "finsight.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Veritabanı tablolarını oluşturur. Uygulama başlangıcında çağrılır."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS manual_news (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'Admin',
                published_at TEXT NOT NULL,
                url TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS rss_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                max_entries INTEGER NOT NULL DEFAULT 10,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS site_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS analyzed_news (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                published_at TEXT NOT NULL,
                url TEXT,
                sentiment TEXT,
                affected_sectors TEXT,      -- JSON string formatında liste
                affected_instruments TEXT,  -- JSON string formatında liste
                impact_summary TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- Varsayılan ayarları ekle (yoksa)
            INSERT OR IGNORE INTO site_settings (key, value) VALUES ('site_title', 'FinSight AI');
            INSERT OR IGNORE INTO site_settings (key, value) VALUES ('site_description', 'Haberlerin Ötesini Görün: Yapay Zeka ile Finansal Duyarlılık ve RSI Takibi.');
            INSERT OR IGNORE INTO site_settings (key, value) VALUES ('max_news', '20');
        """)
        conn.commit()

        # Mevcut RSS kaynaklarını ekle (yoksa)
        default_sources = [
            ("Bloomberg HT", "https://www.bloomberght.com/rss", 15),
            ("Bloomberg HT - Borsa", "https://www.bloomberght.com/rss/borsa", 10),
            ("Bloomberg HT - Döviz", "https://www.bloomberght.com/rss/doviz", 5),
            ("Bloomberg HT - Kripto", "https://www.bloomberght.com/rss/kripto-para", 5),
            ("TRT Haber Ekonomi", "https://www.trthaber.com/ekonomi_articles.rss", 5),
            ("Ekonomim", "https://www.ekonomim.com/rss/rss.xml", 5),
        ]
        for name, url, max_entries in default_sources:
            conn.execute(
                "INSERT OR IGNORE INTO rss_sources (name, url, max_entries) VALUES (?, ?, ?)",
                (name, url, max_entries),
            )
        conn.commit()
    finally:
        conn.close()


# ── RSS Sources CRUD ──────────────────────────────────────────────────

def get_rss_sources(active_only: bool = False) -> List[dict]:
    conn = get_connection()
    try:
        query = "SELECT * FROM rss_sources"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY id"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def add_rss_source(name: str, url: str, max_entries: int = 10) -> dict:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO rss_sources (name, url, max_entries) VALUES (?, ?, ?)",
            (name, url, max_entries),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM rss_sources WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)
    finally:
        conn.close()


def update_rss_source(source_id: int, name: str, url: str, max_entries: int, is_active: bool) -> Optional[dict]:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE rss_sources SET name=?, url=?, max_entries=?, is_active=? WHERE id=?",
            (name, url, max_entries, 1 if is_active else 0, source_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM rss_sources WHERE id = ?", (source_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_rss_source(source_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM rss_sources WHERE id = ?", (source_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ── Manual News CRUD ──────────────────────────────────────────────────

def get_manual_news(active_only: bool = False) -> List[dict]:
    conn = get_connection()
    try:
        query = "SELECT * FROM manual_news"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY published_at DESC"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def add_manual_news(news_id: str, title: str, content: str, source: str, url: str = "") -> dict:
    conn = get_connection()
    try:
        now = datetime.utcnow().isoformat()
        conn.execute(
            "INSERT INTO manual_news (id, title, content, source, published_at, url) VALUES (?, ?, ?, ?, ?, ?)",
            (news_id, title, content, source, now, url),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM manual_news WHERE id = ?", (news_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


def update_manual_news(news_id: str, title: str, content: str, source: str, url: str, is_active: bool) -> Optional[dict]:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE manual_news SET title=?, content=?, source=?, url=?, is_active=? WHERE id=?",
            (title, content, source, url, 1 if is_active else 0, news_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM manual_news WHERE id = ?", (news_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_manual_news(news_id: str) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM manual_news WHERE id = ?", (news_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ── Site Settings ─────────────────────────────────────────────────────

def get_site_settings() -> dict:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT key, value FROM site_settings").fetchall()
        return {row["key"]: row["value"] for row in rows}
    finally:
        conn.close()


def update_site_settings(settings: dict) -> dict:
    conn = get_connection()
    try:
        now = datetime.utcnow().isoformat()
        for key, value in settings.items():
            conn.execute(
                "INSERT OR REPLACE INTO site_settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, str(value), now),
            )
        conn.commit()
        return get_site_settings()
    finally:
        conn.close()


# ── Analyzed News Cache CRUD ──────────────────────────────────────────

def get_cached_news(limit: int = 20) -> List[dict]:
    """Önbelleklenmiş analiz edilmiş haberleri getirir."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM analyzed_news ORDER BY published_at DESC LIMIT ?", 
            (limit,)
        ).fetchall()
        
        import json
        result = []
        for row in rows:
            item = dict(row)
            # JSON string olan listeleri python listesine geri çevir
            try:
                item["affected_sectors"] = json.loads(item["affected_sectors"]) if item["affected_sectors"] else []
            except Exception:
                item["affected_sectors"] = []
                
            try:
                item["affected_instruments"] = json.loads(item["affected_instruments"]) if item["affected_instruments"] else []
            except Exception:
                item["affected_instruments"] = []
                
            result.append(item)
        return result
    finally:
        conn.close()


def save_analyzed_news(
    news_id: str, 
    title: str, 
    content: str, 
    source: str, 
    published_at: str, 
    url: str,
    sentiment: str, 
    affected_sectors: List[str], 
    affected_instruments: List[str], 
    impact_summary: str
) -> bool:
    """Analiz edilmiş haberi analyzed_news tablosuna kaydeder."""
    conn = get_connection()
    try:
        import json
        conn.execute(
            """
            INSERT OR REPLACE INTO analyzed_news 
            (id, title, content, source, published_at, url, sentiment, affected_sectors, affected_instruments, impact_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                news_id, 
                title, 
                content, 
                source, 
                published_at, 
                url, 
                sentiment,
                json.dumps(affected_sectors), 
                json.dumps(affected_instruments), 
                impact_summary
            )
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving analyzed news to DB: {e}")
        return False
    finally:
        conn.close()


def delete_analyzed_news_by_id(news_id: str) -> bool:
    """ID bazlı analiz edilmiş haberi siler."""
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM analyzed_news WHERE id = ?", (news_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def cleanup_old_news(days: int = 7) -> int:
    """Veritabanını temiz tutmak için X günden eski önbelleklenmiş haberleri siler."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM analyzed_news WHERE datetime(published_at) < datetime('now', ?)", 
            (f"-{days} days",)
        )
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Error cleaning up old news: {e}")
        return 0
    finally:
        conn.close()

