import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import os

CHAT_LOG_FILE = "防撞聊天记录.txt"

class ChatLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("群聊记录查看器")
        self.root.geometry("800x600")

        # 搜索框
        self.search_entry = tk.Entry(root, width=60)
        self.search_entry.pack(pady=10)

        self.search_button = tk.Button(root, text="🔍 搜索", command=self.search_text)
        self.search_button.pack()

        # 显示区域
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("微软雅黑", 12))
        self.text_area.pack(expand=True, fill='both')

        # 自动刷新线程
        self.stop_thread = False
        threading.Thread(target=self.auto_refresh, daemon=True).start()

    def read_log_file(self):
        if not os.path.exists(CHAT_LOG_FILE):
            return "📁 聊天记录文件不存在。"
        with open(CHAT_LOG_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def refresh_display(self):
        content = self.read_log_file()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, content)

    def search_text(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showinfo("提示", "请输入关键词再搜索。")
            return
        all_text = self.read_log_file()
        results = [line for line in all_text.splitlines() if keyword in line]
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "\n".join(results) if results else "🔍 没有找到匹配的内容。")

    def auto_refresh(self):
        while not self.stop_thread:
            self.refresh_display()
            time.sleep(10)  # 每 10 秒刷新一次

    def on_close(self):
        self.stop_thread = True
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatLogApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
