import sqlite3

class DBManager:
    def __init__(self, db_path='multiposter.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            title TEXT,
            body TEXT,
            tags TEXT,
            telegram_summary TEXT,
            status TEXT,
            platforms TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            file_path TEXT,
            wp_media_id INTEGER,
            wp_url TEXT,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )''')
        self.conn.commit()

    def add_post(self, topic, title, body, tags, telegram_summary, status, platforms):
        c = self.conn.cursor()
        c.execute('''INSERT INTO posts (topic, title, body, tags, telegram_summary, status, platforms)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (topic, title, body, tags, telegram_summary, status, platforms))
        self.conn.commit()
        return c.lastrowid

    def get_posts(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM posts ORDER BY created_at DESC')
        return c.fetchall() 