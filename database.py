import sqlite3

DB_NAME = 'vondeta.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                serial TEXT,
                approved INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

def save_user(user_id: int, username: str, serial: str):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO users (user_id, username, serial, approved) VALUES (?, ?, ?, ?)',
                  (user_id, username, serial, 0))
        conn.commit()

def get_user_serial(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT serial FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else None

def approve_user(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET approved = 1 WHERE user_id = ?', (user_id,))
        conn.commit()

def reject_user(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET approved = -1 WHERE user_id = ?', (user_id,))
        conn.commit()
