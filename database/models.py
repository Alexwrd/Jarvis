import sqlite3

def create_tables():
    with sqlite3.connect("jarvis.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                full_name TEXT,
                group_name TEXT
            )
        """)
        conn.commit()

def seed_users():
    users = [
        ("@rinxxvv", "Карина", "ege_1"),
        ("@Pdurove_s", "Вячеслав", "ege_1")
    ]
    with sqlite3.connect("jarvis.db") as conn:
        cursor = conn.cursor()
        for username, full_name, group in users:
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, full_name, group_name)
                VALUES (?, ?, ?)
            """, (username, full_name, group))
        conn.commit()