import requests
import os
import sys
from datetime import datetime

# 設定
USER = "kons10"
POSTS_DIR = "dirty/content/post" 

if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR, exist_ok=True)

# 1. 最新のGistを取得
res = requests.get(f"https://api.github.com/users/{USER}/gists?per_page=1")
if not res.ok or not res.json():
    sys.exit(0)

gist = res.json()[0]
gist_id = gist['id']
created_at = gist['created_at'] # 2026-02-16T09:00:00Z
dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

# ファイル名を汐ちゃんのスタイルに合わせる 
filename = f"{dt.year}年{dt.month}月{dt.day}日.md"
filepath = os.path.join(POSTS_DIR, filename)

if os.path.exists(filepath):
    print(f"スキップ：{filename} は既に存在するよ。")
    sys.exit(0)

# 2. ファイル内容の取得と解析
first_file_name = list(gist['files'].keys())[0]
raw_url = gist['files'][first_file_name]['raw_url']
content = requests.get(raw_url).text

# 概要（最初の100文字程度）を抽出してサマリーにする
summary = (gist['description'] or content.split('\n')[0][:100]).replace('"', '\\"')

# 拡張子からタグを推測
ext = first_file_name.split('.')[-1] if '.' in first_file_name else "text"
tags = [ext, "gist"]

# 3. Hugo用のフロントマター (TOML形式 +++) を作成
with open(filepath, "w", encoding="utf-8") as f:
    f.write("+++\n")
    f.write(f"title = \"{summary}\"\n")
    f.write(f"date = '{created_at}'\n")
    f.write(f"gist_id = \"{gist_id}\"\n")
    f.write(f"tags = {tags}\n")
    f.write("draft = false\n")
    f.write("+++\n\n")
    f.write(content)

print(f"自動プロパティ補完で保存したよ: {filename}")
