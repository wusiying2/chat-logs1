import sqlite3
import csv
import os
import datetime

def export_chatlog():
    db_file = "chatlog.db"
    csv_file = "chatlog_export.csv"

    # 连接 SQLite 数据库
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 获取所有聊天记录
    cursor.execute("SELECT * FROM messages")
    rows = cursor.fetchall()

    # 写入 CSV 文件
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "user_id", "message", "timestamp"])
        writer.writerows(rows)

    conn.close()
    print("✅ 导出成功：chatlog_export.csv")

def git_push():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.system("git add chatlog_export.csv")
    os.system(f'git commit -m "📦 自动备份聊天记录 {timestamp}"')
    os.system("git push origin main")
    print("✅ 成功推送到 GitHub 仓库！")

if __name__ == "__main__":
    export_chatlog()
    git_push()
