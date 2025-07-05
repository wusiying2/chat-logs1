import os
import hashlib
import subprocess
import time

LOG_FILE = "防撞聊天记录.txt"
HASH_FILE = ".last_hash"
CHECK_INTERVAL = 30  # 每隔多少秒检测一次

def compute_file_hash(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def load_last_hash():
    if not os.path.exists(HASH_FILE):
        return None
    with open(HASH_FILE, "r") as f:
        return f.read().strip()

def save_last_hash(h):
    with open(HASH_FILE, "w") as f:
        f.write(h)

def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"💬 自动推送聊天记录 {time.strftime('%Y-%m-%d %H:%M:%S')}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ 已推送变更到 GitHub")
    except subprocess.CalledProcessError:
        print("⚠️ Git 推送失败，可能没有变更或冲突")

def main():
    print("🚀 正在启动 Git 自动推送模块，每 30 秒检查一次变更...\n")
    while True:
        current_hash = compute_file_hash(LOG_FILE)
        last_hash = load_last_hash()

        if current_hash and current_hash != last_hash:
            print("📄 检测到聊天记录有新变更，准备推送...")
            save_last_hash(current_hash)
            git_push()
        else:
            print("⏳ 无变更，等待下一轮检测...")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
