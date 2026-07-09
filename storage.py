import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "notifications.db")


def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            date TEXT,
            source TEXT,
            matched BOOLEAN DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS push_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            push_time TEXT,
            count INTEGER,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


def is_exists(notification_id):
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM notifications WHERE id = ?", (notification_id,)).fetchone()
    conn.close()
    return row is not None


def save_notification(notification_id, title, url, date, source, matched=False):
    conn = get_db_connection()
    conn.execute(
        "INSERT OR IGNORE INTO notifications (id, title, url, date, source, matched) VALUES (?, ?, ?, ?, ?, ?)",
        (notification_id, title, url, date, source, matched)
    )
    conn.commit()
    conn.close()


def save_push_log(count, status):
    import datetime
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO push_log (push_time, count, status) VALUES (?, ?, ?)",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, status)
    )
    conn.commit()
    conn.close()


def get_all_notification_ids():
    conn = get_db_connection()
    rows = conn.execute("SELECT id FROM notifications").fetchall()
    conn.close()
    return [row["id"] for row in rows]


def get_recent_notifications(limit=20):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM notifications ORDER BY date DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
