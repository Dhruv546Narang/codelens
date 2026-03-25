"""
database.py
-----------
Handles all SQLite operations for saving and retrieving review history.
Every review is saved automatically — code, language, review result, and timestamp.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "history.db"


def init_db():
    """Create the database and table if they don't exist. Called once on startup."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            language  TEXT NOT NULL,
            code      TEXT NOT NULL,
            review    TEXT NOT NULL,
            score     INTEGER,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_review(language, code, review, score=None):
    """Save a completed review to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reviews (language, code, review, score, created_at) VALUES (?, ?, ?, ?, ?)",
        (language, code, review, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id


def get_history(limit=20):
    """Get the most recent reviews for the sidebar. Returns minimal data (no full code)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, language, substr(code, 1, 80) as preview, score, created_at
        FROM reviews
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id":         row[0],
            "language":   row[1],
            "preview":    row[2].strip().replace("\n", " "),
            "score":      row[3],
            "created_at": row[4]
        }
        for row in rows
    ]


def get_review_by_id(review_id):
    """Fetch a single full review by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, language, code, review, score, created_at FROM reviews WHERE id = ?",
        (review_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id":         row[0],
        "language":   row[1],
        "code":       row[2],
        "review":     row[3],
        "score":      row[4],
        "created_at": row[5]
    }


def delete_review(review_id):
    """Delete a review from history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()


def clear_history():
    """Delete all reviews."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews")
    conn.commit()
    conn.close()
