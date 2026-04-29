import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from utils.config import Config
from utils.logger import logger

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Config.DATABASE_PATH)
        self._init_database()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_bases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_base_id INTEGER NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(512) NOT NULL,
                    file_size INTEGER,
                    file_type VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'pending',
                    chunk_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255),
                    knowledge_base_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE SET NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_kb
                ON documents(knowledge_base_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON chat_messages(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_kb
                ON chat_sessions(knowledge_base_id)
            """)

            conn.commit()
            logger.info("Database initialized successfully")

    def create_knowledge_base(self, name: str, description: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO knowledge_bases (name, description) VALUES (?, ?)",
                (name, description)
            )
            return cursor.lastrowid

    def get_knowledge_bases(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM knowledge_bases ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_knowledge_base(self, kb_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM knowledge_bases WHERE id = ?", (kb_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_knowledge_base(self, kb_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM knowledge_bases WHERE id = ?", (kb_id,))
            return cursor.rowcount > 0

    def create_document(self, kb_id: int, filename: str, file_path: str,
                       file_size: int, file_type: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO documents (knowledge_base_id, filename, file_path, file_size, file_type)
                   VALUES (?, ?, ?, ?, ?)""",
                (kb_id, filename, file_path, file_size, file_type)
            )
            return cursor.lastrowid

    def get_documents(self, kb_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if kb_id:
                cursor.execute(
                    "SELECT * FROM documents WHERE knowledge_base_id = ? ORDER BY created_at DESC",
                    (kb_id,)
                )
            else:
                cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_document_status(self, doc_id: int, status: str,
                              chunk_count: int = 0) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            processed_at = datetime.now().isoformat() if status == "completed" else None
            cursor.execute(
                """UPDATE documents SET status = ?, chunk_count = ?, processed_at = ?
                   WHERE id = ?""",
                (status, chunk_count, processed_at, doc_id)
            )
            return cursor.rowcount > 0

    def delete_document(self, doc_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            return cursor.rowcount > 0

    def create_chat_session(self, title: str = "", kb_id: Optional[int] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if not title:
                title = f"对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            cursor.execute(
                "INSERT INTO chat_sessions (title, knowledge_base_id) VALUES (?, ?)",
                (title, kb_id)
            )
            return cursor.lastrowid

    def get_chat_sessions(self, kb_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if kb_id:
                cursor.execute(
                    "SELECT * FROM chat_sessions WHERE knowledge_base_id = ? ORDER BY updated_at DESC",
                    (kb_id,)
                )
            else:
                cursor.execute("SELECT * FROM chat_sessions ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_chat_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_session_time(self, session_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )

    def delete_chat_session(self, session_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0

    def create_chat_message(self, session_id: int, role: str,
                           content: str, sources: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_messages (session_id, role, content, sources) VALUES (?, ?, ?, ?)",
                (session_id, role, content, sources)
            )
            self.update_session_time(session_id)
            return cursor.lastrowid

    def get_chat_messages(self, session_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

db = Database()
