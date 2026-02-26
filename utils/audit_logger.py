import sqlite3
import json
from datetime import datetime

class AuditLogger:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                data TEXT
            )
        """)
        self.conn.commit()

    def log(self, event_type, data):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, event_type, data) VALUES (?, ?, ?)",
            (datetime.now().isoformat(), event_type, json.dumps(data))
        )
        self.conn.commit()

    def get_daily_summary(self):
        cursor = self.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT event_type, COUNT(*) FROM audit_logs
            WHERE timestamp LIKE ?
            GROUP BY event_type
        """, (f"{today}%",))
        rows = cursor.fetchall()
        return dict(rows)