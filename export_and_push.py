# export_and_push.py
import os
import time
import hashlib
from git import Repo

HASH_RECORD_FILE = "message_hashes.txt"
CHATLOG_FILE = "防撞聊天记录.txt"
LAST_HASH_FILE = ".last_hash"

# 读取旧的 hash
old_hash = ""
if os.path.exists(LAST_HASH_FILE):
    with open(LAST_HASH_FILE, "r", encoding="utf-8") as f:
        old_hash = f.read().strip()

def calculate_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def auto_git_push():
    try:
        new_hash = calculate_file_hash(CHATLOG_FILE)
        if new_hash == old_hash:
            print("⚠️ 没有新变更，跳过推送")
            return

        with open(LAST_HASH_FILE, "w", encoding="utf-8") as f:
            f.write(new_hash)

        repo = Repo(".")
        repo.git.add(CHATLOG_FILE)
        if not repo.is_dirty():
            print("⚠️ 没有需要提交的变更")
            return

        repo.index.commit(f"📄 自动更新聊天记录 {time.strftime('%Y-%m-%d %H:%M:%S')}")
        origin = repo.remote(name="origin")
        origin.push()
        print("✅ 成功推送变更到 GitHub")
    except Exception as e:
        print(f"❌ Git 推送失败: {e}")

if __name__ == "__main__":
    auto_git_push()
