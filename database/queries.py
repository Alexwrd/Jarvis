import sqlite3
import os

DB_PATH = "jarvis.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, group_name FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user  # Вернёт кортеж (id, username, full_name, group_name) или None

def add_user(username: str, full_name: str, group_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, full_name, group_name)
        VALUES (?, ?, ?)
    """, (username, full_name, group_name))
    conn.commit()
    conn.close()

def get_homework_by_group(group_name: str):
    folder = f"files/homework/{group_name}"
    if not os.path.exists(folder):
        return []
    files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    return files

def get_users_by_group(group: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, group_name FROM users WHERE group_name = ?", (group,))
    result = cursor.fetchall()
    conn.close()
    return result

def delete_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()