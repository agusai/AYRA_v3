import sqlite3
import json
from datetime import datetime

DB_PATH = "memory.db"

class MemoryManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        # CHROMA暂时 disabled
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        # Conversations (short‑term)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_message TEXT,
                ayra_response TEXT,
                mood_score REAL,
                model_used TEXT
            )
        """)
        # User profile
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)
        # Social circle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS social_circle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                relationship TEXT,
                last_topic TEXT,
                last_mentioned TEXT
            )
        """)
        # Stories
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                created_at TEXT,
                last_continued TEXT
            )
        """)
        # Dreams
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dreams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dream_text TEXT,
                date TEXT
            )
        """)
        # Stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        """)
        # Audit logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                data TEXT
            )
        """)
        self.conn.commit()

    # ---------- Conversations (short‑term) ----------
    def save_interaction(self, user_msg, ayra_msg, mood_score=0.0, model_used="Gemini"):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (timestamp, user_message, ayra_response, mood_score, model_used) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), user_msg, ayra_msg, mood_score, model_used)
        )
        self.conn.commit()

    def get_recent_conversations(self, limit=5):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_message, ayra_response FROM conversations ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        context = []
        for user, ayra in reversed(rows):
            context.append({"role": "user", "content": user})
            context.append({"role": "assistant", "content": ayra})
        return context

    # ---------- Long‑term memory (暂时 disabled) ----------
    def save_to_vault(self, user_msg, ayra_msg, mood_score, model_used, is_important=False):
        """Long-term memory暂时 disabled"""
        pass  # Do nothing for now

    def search_memories(self, query, n_results=3):
        """Search semantically similar past conversations - 暂时 disabled"""
        return []  # Return empty list

    # ---------- User profile ----------
    def get_profile(self, key):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def set_profile(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute(
            "REPLACE INTO user_profile (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat())
        )
        self.conn.commit()

    # ---------- Social circle ----------
    def add_or_update_person(self, name, relationship, last_topic):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO social_circle (name, relationship, last_topic, last_mentioned)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET
               relationship=excluded.relationship,
               last_topic=excluded.last_topic,
               last_mentioned=excluded.last_mentioned""",
            (name, relationship, last_topic, datetime.now().isoformat())
        )
        self.conn.commit()

    def get_social_circle(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, relationship, last_topic, last_mentioned FROM social_circle")
        rows = cursor.fetchall()
        return [{"name": r[0], "relationship": r[1], "last_topic": r[2], "last_mentioned": r[3]} for r in rows]

    # ---------- Stories ----------
    def save_story(self, title, content):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO stories (title, content, created_at, last_continued) VALUES (?, ?, ?, ?)",
            (title, content, datetime.now().isoformat(), datetime.now().isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_story(self, story_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, content FROM stories WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        return {"title": row[0], "content": row[1]} if row else None

    def get_latest_story(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, content FROM stories ORDER BY last_continued DESC LIMIT 1")
        row = cursor.fetchone()
        return {"id": row[0], "title": row[1], "content": row[2]} if row else None

    def update_story(self, story_id, new_content):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE stories SET content = content || ? , last_continued = ? WHERE id = ?",
            (new_content, datetime.now().isoformat(), story_id)
        )
        self.conn.commit()

    # ---------- Dreams ----------
    def save_dream(self, dream_text):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO dreams (dream_text, date) VALUES (?, ?)",
            (dream_text, datetime.now().isoformat())
        )
        self.conn.commit()

    def get_random_dream(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT dream_text FROM dreams ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else None

    # ---------- Stats ----------
    def increment_stat(self, key, inc=1):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES (?, 0)", (key,))
        cursor.execute("UPDATE user_stats SET value = value + ? WHERE key = ?", (inc, key))
        self.conn.commit()

    def get_stat(self, key):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM user_stats WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else 0

    def set_stat(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO user_stats (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    # ---------- Audit logs ----------
    def log_audit(self, event_type, data):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, event_type, data) VALUES (?, ?, ?)",
            (datetime.now().isoformat(), event_type, json.dumps(data))
        )
        self.conn.commit()