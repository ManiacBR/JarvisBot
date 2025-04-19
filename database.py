import sqlite3
from datetime import datetime
import tiktoken

class ConversationDatabase:
    def __init__(self, db_name="conversations.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()
        self.conn.execute("PRAGMA journal_mode=WAL;")

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    guild_id TEXT,
                    message TEXT,
                    role TEXT,
                    timestamp DATETIME,
                    PRIMARY KEY (guild_id, timestamp, role, message)
                )
            """)

    def save_message(self, guild_id, message, role):
        with self.conn:
            self.conn.execute(
                "INSERT INTO conversations (guild_id, message, role, timestamp) VALUES (?, ?, ?, ?)",
                (guild_id, message, role, datetime.now())
            )

    def get_context(self, guild_id, max_tokens=100000, model='gpt-4.1-2025-04-14'):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, message FROM conversations WHERE guild_id = ? ORDER BY timestamp ASC",
            (guild_id,)
        )
        rows = cursor.fetchall()
        context = [{"role": r, "content": m} for r, m in rows]
        encoding = tiktoken.encoding_for_model(model)
        while context and sum(len(encoding.encode(c["content"])) for c in context) > max_tokens:
            context.pop(0)
        return context

    def clear_context(self, guild_id):
        with self.conn:
            self.conn.execute(
                "DELETE FROM conversations WHERE guild_id = ?", (guild_id,)
            )
