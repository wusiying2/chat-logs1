import os
import requests
from flask import Flask, request, abort

app = Flask(__name__)

# LINE官方提供的验证信息
CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

# 获取消息的URL
LINE_API_URL = 'https://api.line.me/v2/bot/message/reply'

@app.route("/callback", methods=['POST'])
def callback():
    # 获取Webhook请求的消息体
    body = request.get_data(as_text=True)
    print(f"Request body: {body}")

    # 如果没有正确的请求方法，抛出异常
    if request.method != 'POST':
        abort(400)

    try:
        # 解析JSON数据
        data = request.json
        events = data.get('events', [])

        # 遍历所有事件
        for event in events:
            # 获取消息类型
            if event['type'] == 'message':
                user_message = event['message']['text']
                user_id = event['source']['userId']
                
                # 输出用户发送的消息
                print(f"Received message: {user_message} from user: {user_id}")

                # 回复消息
                reply_token = event['replyToken']
                reply_message = f"你刚刚发送了: {user_message}"

                reply(reply_token, reply_message)

    except Exception as e:
        print(f"Error: {e}")
        abort(500)

    return 'OK'

# 发送回复消息的函数
def reply(reply_token, message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }

    payload = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': message}]
    }

    # 发送请求
    response = requests.post(LINE_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")

if __name__ == "__main__":
    # 设置Flask应用监听端口
    app.run(port=5000)
