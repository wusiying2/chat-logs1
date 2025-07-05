import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit, QSpinBox
)
from PyQt6.QtCore import QTimer

class ChatLogViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("聊天记录查看器 - MoodFitAI")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # 链接输入和刷新倒计时
        self.url_layout = QHBoxLayout()
        self.url_input = QLineEdit("https://raw.githubusercontent.com/wusiying2/chat-logs/main/%E9%98%B2%E6%92%9E%E8%81%8A%E5%A4%A9%E8%AE%B0%E5%BD%95.txt")
        self.refresh_button = QPushButton("立即刷新")
        self.url_layout.addWidget(QLabel("聊天记录链接:"))
        self.url_layout.addWidget(self.url_input)
        self.url_layout.addWidget(self.refresh_button)

        # 搜索功能
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_button = QPushButton("搜索")
        self.search_layout.addWidget(QLabel("关键词:"))
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)

        # 倒计时与间隔设置
        self.timer_layout = QHBoxLayout()
        self.timer_label = QLabel("下次刷新倒计时: 5 秒")
        self.interval_input = QSpinBox()
        self.interval_input.setMinimum(2)
        self.interval_input.setMaximum(3600)
        self.interval_input.setValue(5)
        self.timer_layout.addWidget(QLabel("刷新间隔(秒):"))
        self.timer_layout.addWidget(self.interval_input)
        self.timer_layout.addWidget(self.timer_label)

        # 文本区域
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        # 加入布局
        self.layout.addLayout(self.url_layout)
        self.layout.addLayout(self.search_layout)
        self.layout.addLayout(self.timer_layout)
        self.layout.addWidget(self.text_area)

        self.setLayout(self.layout)

        # 定时器设置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_chatlog)
        self.timer.start(5000)

        self.countdown = 5
        self.count_timer = QTimer(self)
        self.count_timer.timeout.connect(self.update_countdown)
        self.count_timer.start(1000)

        # 事件连接
        self.refresh_button.clicked.connect(self.refresh_chatlog)
        self.search_button.clicked.connect(self.search_keyword)
        self.interval_input.valueChanged.connect(self.update_interval)

    def update_interval(self):
        new_interval = self.interval_input.value() * 1000
        self.timer.setInterval(new_interval)
        self.countdown = self.interval_input.value()

    def update_countdown(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self.countdown = self.interval_input.value()
        self.timer_label.setText(f"下次刷新倒计时: {self.countdown} 秒")

    def refresh_chatlog(self):
        url = self.url_input.text()
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                self.text_area.setPlainText(response.text)
        except Exception as e:
            self.text_area.setPlainText(f"❌ 无法加载聊天记录: {str(e)}")

    def search_keyword(self):
        keyword = self.search_input.text()
        if keyword:
            content = self.text_area.toPlainText()
            results = [line for line in content.splitlines() if keyword in line]
            self.text_area.setPlainText("\n".join(results) if results else "🔍 未找到任何匹配项")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ChatLogViewer()
    viewer.show()
    sys.exit(app.exec())
