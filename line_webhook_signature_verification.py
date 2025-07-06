import os
import hmac
import hashlib
import base64
from flask import Flask, request, abort
from dotenv import load_dotenv
import subprocess
from datetime import datetime

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 从 .env 文件中获取LINE的Channel Secret
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# 确保环境变量正确加载
if not CHANNEL_SECRET:
    print("Error: Missing LINE credentials in .env file.")
    exit(1)

# 设置聊天记录文件的路径
LOG_FILE_PATH = 'chat_logs.txt'

# 设置Webhook回调处理
@app.route('/callback', methods=['POST'])
def callback():
    # 获取请求头中的签名
    signature = request.headers.get('X-Line-Signature')  # 获取签名
    body = request.get_data(as_text=True)  # 获取请求体

    # 调试输出
    print(f"Request body: {body}")
    print(f"X-Line-Signature: {signature}")

    # 使用Channel Secret生成预期的签名
    hashed = hmac.new(CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256)
    expected_signature = base64.b64encode(hashed.digest()).decode()

    # 调试输出
    print(f"Expected Signature: {expected_signature}")

    # 如果签名不匹配，返回400错误
    if signature != expected_signature:
        print("Signature mismatch!")
        abort(400)

    # 签名验证通过，处理消息
    print("Signature verified successfully.")
    print(f"Received message: {body}")

    # 解析事件中的消息并保存到本地文件
    events = request.json['events']
    messages = []
    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            user_message = event['message']['text']  # 获取用户发送的消息
            user_id = event['source']['userId']
            timestamp = datetime.utcfromtimestamp(event['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            
            message_data = f"[{timestamp}] {user_id}: {user_message}\n"
            messages.append(message_data)

    # 将聊天记录保存到本地TXT文件
    if messages:
        save_chat_log(messages)
        push_to_github()

    return 'OK'

def save_chat_log(messages):
    # 将聊天记录保存到本地文件（追加写入）
    try:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.writelines(messages)
        print(f"Chat logs saved to {LOG_FILE_PATH}")  # 确保文件写入成功
    except Exception as e:
        print(f"Error saving chat logs: {e}")

def push_to_github():
    # 在本地git仓库中提交并推送聊天记录
    try:
        # 添加文件到git仓库
        subprocess.run(['git', 'add', LOG_FILE_PATH], check=True)

        # 提交更改
        commit_message = f"Add new chat log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # 推送更改到GitHub仓库
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

        print("Chat log successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while pushing to GitHub: {e}")

if __name__ == '__main__':
    app.run(port=5000)  # 启动Flask应用，监听5000端口
