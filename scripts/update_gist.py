import requests
import os
import sys
from datetime import datetime
from janome.tokenizer import Tokenizer
from collections import Counter

# --- 設定 ---
USER = "kons10"
POSTS_DIR = "dirty/content/post" 
TARGET_KEYWORDS = [
    "python", "linux", "hugo", "javascript", "js", "github", 
    "docker", "windows", "amd", "ryzen", "gpu", "git", "bash",
    "material", "design", "web", "iframe"
]

if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR, exist_ok=True)

# --- タグ発掘関数 ---
def extract_tags_from_content(text, filename):
    t = Tokenizer()
    found_tags = []
    
    # 拡張子も一応タグ候補に入れる
    ext = filename.split('.')[-1] if '.' in filename else "text"
    found_tags.append(ext.lower())
    found_tags.append("gist")

    # 本文から発掘
    for token in t.tokenize(text):
        original_word = token.surface
        lower_word = original_word.lower()
        pos = token.part_of_speech.split(',')
        
        # 指定キーワードに一致するか
        if lower_word in TARGET_KEYWORDS:
            found_tags.append(lower_word)
        # 4文字以上の英単語の固有名詞も自動で拾う（アイコ対策で長めに設定）
        elif pos[0] == "名詞" and pos[1] == "固有名詞":
            if original_word.isalnum() and len(original_word) >= 4:
                found_tags.append(lower_word)

    # 重複を消してリストにする
    return list(set(found_tags))

# --- 1. 最新のGistを取得 ---
res = requests.get(f"https://api.github.com/users/{USER}/gists?per_page=1")
if not res.ok or not res.json():
    print("Gistが見つからなかったよ。")
    sys.exit(0)

gist = res.json()[0]
gist_id = gist['id']
created_at = gist['created_at']
dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

filename = dt.strftime("%Y年%m月%d日.md")
filepath = os.path.join(POSTS_DIR, filename)

if os.path.exists(filepath):
    print(f"スキップ：{filename} は既に存在するよ。")
    sys.exit(0)

# --- 2. 内容の取得とタグ発掘 ---
first_file_name = list(gist['files'].keys())[0]
raw_url = gist['files'][first_file_name]['raw_url']
content = requests.get(raw_url).text

# ！！！ここがアップグレード箇所！！！
tags = extract_tags_from_content(content, first_file_name)

# 概要
summary = (gist['description'] or content.split('\n')[0][:100]).replace('"', '\\"')

# --- 3. Hugo用のフロントマター作成 ---
with open(filepath, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write(f"title: \"{summary}\"\n")
    f.write(f"date: {created_at}\n")
    f.write(f"gist_id: \"{gist_id}\"\n")
    f.write(f"tags: {tags}\n") # 発掘されたタグが入るよ！
    f.write("draft: false\n")
    f.write("---\n\n")
    f.write(content)

print(f"完了！タグ {tags} を付けて保存したよ: {filename}")
