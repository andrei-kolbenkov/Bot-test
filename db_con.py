import sqlite3

def init_db():
    conn = sqlite3.connect('sites.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        xpath TEXT NOT NULL
    )
    ''')
    conn.commit()
    return conn, cursor

def save_to_db(cursor, title, url, xpath):
    cursor.execute('''
    INSERT INTO sites (title, url, xpath) VALUES (?, ?, ?)
    ''', (title, url, xpath))
    cursor.connection.commit()