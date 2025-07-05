from flask import Flask, request, abort
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage
from linebot.v3 import WebhookHandler

import sqlite3
import datetime

app = Flask(__name__)

# ✅ 你的 LINE Bot 密钥
CHANNEL_SECRET = "abe79d90d2809e5cdd68c95861d8f157"
CHANNEL_ACCESS_TOKEN = "GStbnfuzcKJ/jjwuoIREu99P8grH0LRoZACmdv7r1a8OvaxGCpJxDeS5OGfhYNACE87rfSsgL7YHGdy11O/+rYDejf8BWnjZwyV0HBC9/VIgZveoGFD0Hqrabxi9VGro//tFuFfEG577WUO3kFDvTAdB04t89/1O/w1cDnyilFU="

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ✅ 保存聊天记录到 SQLite
def save_message_to_db(user_id, message_text):
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
    cursor.execute('''
        INSERT INTO messages (user_id, message, timestamp)
        VALUES (?, ?, ?)
    ''', (user_id, message_text, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ✅ Webhook 接收入口
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("❌ Webhook 错误:", e)
        print("📦 请求内容:", body)
        abort(400)

    return "OK"

# ✅ 处理用户消息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text

    print(f"✅ 收到用户消息：{msg}（来自用户：{user_id}）")

    # 保存到数据库
    save_message_to_db(user_id, msg)

    # 回复用户（必须加 type="text"）
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=[
                TextMessage(type="text", text=f"你说了：{msg}")
            ]
        )

if __name__ == "__main__":
    app.run(port=5000)
