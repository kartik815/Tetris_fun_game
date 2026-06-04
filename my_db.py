import sqlite3

conn = sqlite3.connect("game.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    score INTEGER NOT NULL
)
""")

def save_score(data):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO leaderboard (username, score) VALUES (?, ?)",
        data)
    conn.commit()
# res = cursor.execute("SELECT name FROM sqlite_master")
# print(res.fetchone())

# data = [("Kartik", 300), ("Krishna", 400)]


# save_score(data)

# cursor.execute("DROP TABLE IF EXISTS leaderboard")
# res = cursor.execute("SELECT username, score FROM leaderboard")
# print(res.fetchall())
conn.commit()
# conn.close()
