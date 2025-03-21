import sqlite3
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime
import csv

from ext_llm.scheduler_statistic import SchedulerStatistic


class SchedulerStatisticRepository:
    def __init__(self, db_path: str = "scheduler_statistic.db"):
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
            CREATE TABLE IF NOT EXISTS scheduler_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                max_workers INTEGER,
                max_retries_per_request INTEGER,
                start_time TEXT,
                stop_time TEXT,
                total_requests INTEGER,
                successful_requests INTEGER,
                failed_requests INTEGER,
                average_response_time REAL,
                throughput REAL,
                retries_count INTEGER,
                average_retries_per_request REAL
            )
            """)

    def save(self, statistic: SchedulerStatistic) -> int:
        """Save a scheduler statistic to the database and return its ID."""
        conn = self._get_connection()

        with conn:
            cursor = conn.execute("""
            INSERT INTO scheduler_statistics (
                created_at, max_workers, max_retries_per_request, start_time,
                stop_time, total_requests, successful_requests, failed_requests,
                average_response_time, throughput, retries_count, average_retries_per_request
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                statistic.max_workers,
                statistic.max_retries_per_request,
                statistic.start_time.isoformat() if statistic.start_time else None,
                statistic.stop_time.isoformat() if statistic.stop_time else None,
                statistic.total_requests,
                statistic.successful_requests,
                statistic.failed_requests,
                statistic.average_response_time,
                statistic.throughput,
                statistic.retries_count,
                statistic.average_retries_per_request
            ))
            return cursor.lastrowid

    def find_by_id(self, stat_id: int) -> Optional[Dict[str, Any]]:
        """Find a scheduler statistic by its ID."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM scheduler_statistics WHERE id = ?", (stat_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def find_all(self) -> List[Dict[str, Any]]:
        """Get all scheduler statistics."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM scheduler_statistics ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def find_by_time_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Find statistics within a time range."""
        conn = self._get_connection()
        cursor = conn.execute("""
        SELECT * FROM scheduler_statistics 
        WHERE created_at >= ? AND created_at <= ? 
        ORDER BY created_at DESC
        """, (start_date.isoformat(), end_date.isoformat()))
        return [dict(row) for row in cursor.fetchall()]

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics across all records."""
        conn = self._get_connection()
        cursor = conn.execute("""
        SELECT 
            AVG(average_response_time) as avg_response_time,
            AVG(throughput) as avg_throughput,
            AVG(average_retries_per_request) as avg_retries,
            SUM(total_requests) as total_requests,
            SUM(successful_requests) as successful_requests,
            SUM(failed_requests) as failed_requests,
            COUNT(*) as sample_count
        FROM scheduler_statistics
        """)
        row = cursor.fetchone()
        return dict(row) if row else None

    def export_to_csv(self, file_path: str = None) -> str:
        """Export all statistics to a CSV file."""
        if file_path is None:
            file_path = f"scheduler_stats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM scheduler_statistics")

        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            # Get column names from cursor description
            columns = [column[0] for column in cursor.description]
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()

            # Write all rows
            for row in cursor:
                writer.writerow(dict(row))

        return file_path

    def delete_old_records(self, days_to_keep: int = 30) -> int:
        """Delete records older than the specified number of days."""
        conn = self._get_connection()
        cutoff_date = (datetime.now() - datetime.timedelta(days=days_to_keep)).isoformat()

        with conn:
            cursor = conn.execute("""
            DELETE FROM scheduler_statistics 
            WHERE created_at < ?
            """, (cutoff_date,))
            return cursor.rowcount

    def close(self):
        """Close the database connection if it exists."""
        if hasattr(self.connection_local, "conn"):
            self.connection_local.conn.close()
            delattr(self.connection_local, "conn")