import sqlite3
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime

from ext_llm.llm.response import Response

class ResponseRepository:
    def __init__(self, db_path: str = "llm_responses.db"):
        """Initialize the repository with a SQLite database path."""
        self.db_path = db_path
        self.connection_local = threading.local()
        self._init_db()

    def _get_connection(self):
        """Get or create a thread-local database connection."""
        if not hasattr(self.connection_local, "conn"):
            self.connection_local.conn = sqlite3.connect(self.db_path)
            # Enable foreign keys and return rows as dictionaries
            self.connection_local.conn.execute("PRAGMA foreign_keys = ON")
            self.connection_local.conn.row_factory = sqlite3.Row
        return self.connection_local.conn

    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        conn = self._get_connection()
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                content TEXT NOT NULL,
                system_prompt TEXT,
                user_prompt TEXT,
                preset_name TEXT,
                model_id TEXT,
                latency REAL,
                finish_reason TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                temperature REAL,
                max_tokens INTEGER
            )
            """)

    def save(self, response: Response, system_prompt: str = None, user_prompt: str = None) -> int:
        """Save a response to the database and return its ID."""
        conn = self._get_connection()
        metadata = response.metadata or {}

        with conn:
            cursor = conn.execute("""
            INSERT INTO responses (
                timestamp, content, system_prompt, user_prompt, preset_name, 
                model_id, latency, finish_reason, prompt_tokens,
                completion_tokens, total_tokens, temperature, max_tokens
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                str(response.content),
                system_prompt,
                user_prompt,
                metadata.get('preset_name'),
                metadata.get('model_id'),
                metadata.get('latency'),
                metadata.get('finish_reason'),
                metadata.get('prompt_tokens'),
                metadata.get('completion_tokens'),
                metadata.get('total_tokens'),
                metadata.get('temperature'),
                metadata.get('max_tokens')
            ))
            return cursor.lastrowid

    def find_by_id(self, response_id: int) -> Optional[Dict[str, Any]]:
        """Find a response by its ID."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM responses WHERE id = ?", (response_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def find_all(self) -> List[Dict[str, Any]]:
        """Get all responses."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM responses ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]

    def find_by_model(self, model_id: str) -> List[Dict[str, Any]]:
        """Find responses by model ID."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM responses WHERE model_id = ? ORDER BY timestamp DESC", (model_id,))
        return [dict(row) for row in cursor.fetchall()]

    def find_by_preset(self, preset_name: str) -> List[Dict[str, Any]]:
        """Find responses by preset name."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM responses WHERE preset_name = ? ORDER BY timestamp DESC", (preset_name,))
        return [dict(row) for row in cursor.fetchall()]

    def export_to_csv(self, file_path: str = None) -> str:
        """Export all responses to a CSV file."""
        import csv

        if file_path is None:
            file_path = f"llm_responses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM responses")

        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            # Get column names from cursor description
            columns = [column[0] for column in cursor.description]
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()

            # Write all rows
            for row in cursor:
                writer.writerow(dict(row))

        return file_path

    def close(self):
        """Close the database connection if it exists."""
        if hasattr(self.connection_local, "conn"):
            self.connection_local.conn.close()
            delattr(self.connection_local, "conn")