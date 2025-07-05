import sqlite3

conn = sqlite3.connect("chatlog.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        message TEXT,
        timestamp TEXT
    )
''')
conn.commit()
conn.close()

print("✅ 数据库初始化完成，已创建 messages 表。")
