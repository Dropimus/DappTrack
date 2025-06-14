# database.py
import sqlite3

conn = sqlite3.connect("posts.db")
cursor = conn.cursor()

# Create the posts table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT,
    content TEXT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def save_post(channel, content):
    cursor.execute("INSERT INTO posts (channel, content) VALUES (?, ?)", (channel, content))
    conn.commit()
