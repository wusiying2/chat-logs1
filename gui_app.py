import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLineEdit, QLabel, QHBoxLayout
)
from PyQt6.QtCore import QTimer, Qt
from threading import Thread
from export_and_push import push_once, auto_push_loop

class ChatLogApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("实时聊天记录查看器")
        self.resize(800, 600)

        layout = QVBoxLayout()

        # 地址输入
        self.url_input = QLineEdit("https://raw.githubusercontent.com/wusiying2/chat-logs/main/防撞聊天记录.txt")
        layout.addWidget(QLabel("🔗 GitHub 原始地址："))
        layout.addWidget(self.url_input)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 输入关键词进行搜索...")
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_logs)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # 显示聊天记录
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # 底部按钮
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔁 立即刷新")
        self.refresh_btn.clicked.connect(self.load_logs)

        self.push_btn = QPushButton("🚀 立即推送")
        self.push_btn.clicked.connect(self.manual_push)

        self.status_label = QLabel("⏱ 正在启动...")

        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.push_btn)
        btn_layout.addWidget(self.status_label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_logs)
        self.timer.start(5000)  # 每5秒刷新

        # 启动后台自动推送线程
        Thread(target=auto_push_loop, daemon=True).start()

        # 初始化加载
        self.load_logs()

    def load_logs(self):
        url = self.url_input.text()
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.text_area.setPlainText(response.text)
                self.status_label.setText("✅ 已刷新")
            else:
                self.status_label.setText(f"❌ 获取失败: 状态码 {response.status_code}")
        except Exception as e:
            self.status_label.setText(f"❌ 请求错误: {str(e)}")

    def search_logs(self):
        keyword = self.search_input.text()
        all_text = self.text_area.toPlainText()
        if keyword:
            matched_lines = "\n".join([line for line in all_text.splitlines() if keyword in line])
            self.text_area.setPlainText(matched_lines or "⚠️ 没有匹配结果")
            self.status_label.setText("🔍 搜索完成")
        else:
            self.load_logs()

    def manual_push(self):
        self.status_label.setText("🚀 正在推送中...")
        Thread(target=self._push_thread, daemon=True).start()

    def _push_thread(self):
        success = push_once()
        self.status_label.setText("✅ 推送成功" if success else "⚠️ 无需推送")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatLogApp()
    window.show()
    sys.exit(app.exec())
