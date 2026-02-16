import requests
import os
import sys

# 設定（自分の環境に合わせてね）
USER = "kons10"  # 汐ちゃんのID
POSTS_DIR = "content/posts"

# 1. 最新のGistを1件だけ取得
res = requests.get(f"https://api.github.com/users/{USER}/gists?per_page=1")
if not res.ok or not res.json():
    print("Gistが見つからなかったよ。")
    sys.exit(0)

gist = res.json()[0]
gist_id = gist['id']
created_at = gist['created_at']  # 例: 2026-02-16T09:00:00Z
date_str = created_at.split('T')[0] # 2026-02-16

# 2. 重複チェック（ファイル名に日付やIDを含めて管理）
filename = f"gist-{date_str}-{gist_id}.md"
filepath = os.path.join(POSTS_DIR, filename)

if os.path.exists(filepath):
    print(f"スキップ：{filename} は既に存在するよ。")
    sys.exit(0) # 正常終了（キャンセル扱い）

# 3. ファイル作成（最新の1ファイル目を取得）
first_file_name = list(gist['files'].keys())[0]
raw_url = gist['files'][first_file_name]['raw_url']
content = requests.get(raw_url).text

description = gist['description'] or first_file_name

# Hugo用フロントマター付きで保存
with open(filepath, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write(f"title: \"{description}\"\n")
    f.write(f"date: {created_at}\n")
    f.write(f"gist_id: \"{gist_id}\"\n")
    f.write("---\n\n")
    f.write(content)

print(f"新着Gistを保存したよ: {filename}")
