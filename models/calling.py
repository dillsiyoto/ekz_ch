import sqlite3

conn = sqlite3.connect('calling.db')
cursor = conn.cursor()

cursor.execute('''
            CREATE TABLE IF NOT EXISTS calling(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               doctor TEXT,
               day TEXT,
               time TEXT
            )
''')

conn.commit()
conn.close()