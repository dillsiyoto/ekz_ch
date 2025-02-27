import sqlite3

conn = sqlite3.connect('post.db')
cursor = conn.cursor()

cursor.execute('''
            CREATE TABLE IF NOT EXISTS post(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL UNIQUE,
               description TEXT NOT NULL,
               price INTEGER,
               file_path TEXT
            )
''')

conn.commit()
conn.close()