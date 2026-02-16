import requests
import os
import sys
from datetime import datetime

# 設定
USER = "kons10"
POSTS_DIR = "dirty/content/post" 

if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR, exist_ok=True)

# [cite_start]1. 最新のGistを取得 [cite: 13, 20]
res = requests.get(f"https://api.github.com/users/{USER}/gists?per_page=1")
if not res.ok or not res.json():
    sys.exit(0)

gist = res.json()[0]
gist_id = gist['id']
[cite_start]created_at = gist['created_at'] # 2026-02-16T09:00:00Z [cite: 13, 20]
dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

# --- ここを修正：0埋めの形式にする ---
# %m は月(01-12)、%d は日(01-31)を2桁で出すよ
filename = dt.strftime("%Y年%m月%d日.md")
# ----------------------------------

filepath = os.path.join(POSTS_DIR, filename)

if os.path.exists(filepath):
    print(f"スキップ：{filename} は既に存在するよ。")
    sys.exit(0)

# [cite_start]2. ファイル内容の取得と解析 [cite: 13, 20]
first_file_name = list(gist['files'].keys())[0]
raw_url = gist['files'][first_file_name]['raw_url']
content = requests.get(raw_url).text

# 概要を抽出
summary = (gist['description'] or content.split('\n')[0][:100]).replace('"', '\\"')

# [cite_start]拡張子からタグを推測 [cite: 13, 20]
ext = first_file_name.split('.')[-1] if '.' in first_file_name else "text"
tags = [ext, "gist"]

# [cite_start]3. Hugo用のフロントマター (---) を作成 [cite: 13, 20]
with open(filepath, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write(f"title = \"{summary}\"\n")
    f.write(f"date = '{created_at}'\n")
    f.write(f"gist_id = \"{gist_id}\"\n")
    f.write(f"tags = {tags}\n")
    f.write("draft = false\n")
    f.write("---\n\n")
    f.write(content)

print(f"0埋め日付形式で保存したよ: {filename}")
