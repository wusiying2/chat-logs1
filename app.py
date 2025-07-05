import os
import hashlib
import sqlite3
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 加载 .env
load_dotenv()
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")

# 初始化 LINE API
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# 初始化 Flask
app = Flask(__name__)

# 文件路径
CHATLOG_PATH = "防撞聊天记录.txt"
HASH_PATH = "message_hashes.txt"
DB_PATH = "chatlogs.db"

# 初始化数据库
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                text TEXT,
                timestamp INTEGER,
                UNIQUE(user_id, text, timestamp)
            )
        """)
        conn.commit()

init_db()

# 哈希去重
def load_hashes():
    if os.path.exists(HASH_PATH):
        with open(HASH_PATH, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def save_hash(hash_value):
    with open(HASH_PATH, "a", encoding="utf-8") as f:
        f.write(hash_value + "\n")

def hash_message(user_id, text, timestamp):
    return hashlib.sha256(f"{user_id}|{text}|{timestamp}".encode("utf-8")).hexdigest()

# 保存消息
def save_message(user_id, text, timestamp):
    log_line = f"[{timestamp}] {user_id}: {text}"
    with open(CHATLOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO messages (user_id, text, timestamp) VALUES (?, ?, ?)",
                       (user_id, text, timestamp))
        conn.commit()

# Webhook 路由
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# 消息处理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id if event.source.user_id else "Unknown"
    text = event.message.text
    timestamp = event.timestamp

    msg_hash = hash_message(user_id, text, timestamp)
    hashes = load_hashes()
    if msg_hash in hashes:
        print("跳过重复消息")
        return

    save_message(user_id, text, timestamp)
    save_hash(msg_hash)

if __name__ == "__main__":
    app.run(port=8000)
