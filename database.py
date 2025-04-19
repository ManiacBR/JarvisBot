import sqlite3
from datetime import datetime

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

    def get_context(self, guild_id, max_messages=40):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, message FROM conversations WHERE guild_id = ? ORDER BY timestamp ASC",
            (guild_id,)
        )
        rows = cursor.fetchall()
        context = [{"role": role, "content": msg} for role, msg in rows]
        if len(context) > max_messages:
            context = context[-max_messages:]
        return context

    def clear_context(self, guild_id):
        with self.conn:
            self.conn.execute(
                "DELETE FROM conversations WHERE guild_id = ?", (guild_id,)
            )
