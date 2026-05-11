import sqlite3
from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
)

def init_db():

    conn = sqlite3.connect('medichat.db')

    c = conn.cursor()

    # USERS TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    ''')

    # CHAT HISTORY
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT,
            bot_reply TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id)
            REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


def get_db():

    conn = sqlite3.connect('medichat.db')

    conn.row_factory = sqlite3.Row

    # ENABLE FOREIGN KEYS
    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


def hash_password(password):

    return generate_password_hash(password)


# INITIALIZE DATABASE
init_db()