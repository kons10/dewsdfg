import requests
import os
import sys
import re
from datetime import datetime
from janome.tokenizer import Tokenizer
from collections import Counter
from pathlib import Path
from gliclass import GLiClassModel, ZeroShotClassificationPipeline

# ========== 設定 ==========
USER = "kons10"
POSTS_DIR = "dirty/content/post"

# デフォルトのタグ候補（既存タグがまだ少ないとき用 / フォールバック）
DEFAULT_CANDIDATE_TAGS = [
    "python", "linux", "hugo", "javascript", "js", "github",
    "docker", "windows", "amd", "ryzen", "gpu", "git", "bash",
    "material", "design", "web", "iframe", "code", "api", "cli",
    "rust", "go", "java", "c++", "ruby", "php", "sql", "nosql",
    "aws", "azure", "gcp", "terraform", "kubernetes", "jenkins",
    # 非テック用（これらはスコアが高ければ選択されるが、新タグは抑制される）
    "cooking", "recipe", "life", "diary", "health", "travel", "movie", "music"
]

# 非テックとみなすカテゴリ（スコア優先度を下げるために使うわけではないが、ログ用）
NON_TECH_TAGS = {"cooking", "recipe", "life", "diary", "health", "travel", "movie", "music"}

# ストップワード（新タグ生成時のみ）
STOPWORDS = {"これ", "それ", "あれ", "こと", "もの", "ところ", "よう", "そう", "できる", "なる", "する"}

# GLiClass モデル（グローバルにキャッシュ）
_model = None

def get_classifier():
    global _model
    if _model is None:
        # 軽量モデルを指定。初回実行時にダウンロードされる（GitHub Actions でも動作可）
        model = GLiClassModel.from_pretrained("knowledgator/gliclass-small-v3.0")
        _model = ZeroShotClassificationPipeline(model, device=-1)  # device=-1 で CPU
    return _model

# ========== 既存タグの収集 ==========
def load_existing_tags():
    tags = set()
    post_dir = Path(POSTS_DIR)
    if not post_dir.exists():
        return tags

    for md_file in post_dir.glob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"^tags:\s*\[(.*?)\]", content, re.MULTILINE)
                if match:
                    tag_list = match.group(1).split(",")
                    for tag in tag_list:
                        cleaned = tag.strip().strip("'\"")
                        if cleaned:
                            tags.add(cleaned)
        except Exception as e:
            print(f"警告: {md_file} の読み込み中にエラー: {e}")
    return tags

# ========== コードブロック検出 ==========
def has_code_block(content):
    return "```" in content

# ========== GLiClass による分類 ==========
def classify_tags(content, candidate_tags):
    """候補タグリストから最適なタグを最大3個まで返す（閾値 0.3 以上）"""
    if not candidate_tags:
        return []

    classifier = get_classifier()
    # テキストが長い場合は先頭 1500 文字程度に切り詰め（パフォーマンス対策）
    text = content[:1500] if len(content) > 1500 else content

    result = classifier(text, candidate_tags, multi_label=True)  # 複数タグ許容

    # スコアが高い順に並べ、0.3 以上のタグを選ぶ
    selected = []
    for tag, score in zip(result["labels"], result["scores"]):
        if score >= 0.3 and tag not in selected:
            selected.append(tag)
        if len(selected) >= 3:  # 最大3タグまで
            break
    return selected

# ========== 非テック内容の判定（補助的） ==========
def is_non_tech_content(content):
    """簡単なキーワードチェック。テック要素が薄く非テック要素があれば True"""
    if "```" in content:
        return False

    tech_keywords = {"python", "linux", "docker", "github", "javascript", "code", "api"}
    non_tech_keywords = {"料理", "レシピ", "人生", "日記", "健康", "旅行", "映画", "音楽", "趣味"}

    lower_content = content.lower()
    tech_count = sum(1 for kw in tech_keywords if kw in lower_content)
    non_tech_count = sum(1 for kw in non_tech_keywords if kw in content)

    return tech_count < 2 and non_tech_count >= 1

def generate_new_tags_from_content(content, existing_tags, limit=2):
    """非テック内容から頻出名詞を最大 limit 個、新タグとして生成（既存になければ）"""
    t = Tokenizer()
    word_counts = Counter()
    for token in t.tokenize(content):
        pos = token.part_of_speech.split(',')
        if pos[0] == "名詞" and pos[1] in ("一般", "固有名詞"):
            word = token.surface
            if 2 <= len(word) <= 10 and word not in STOPWORDS:
                word_counts[word] += 1

    new_tags = []
    for word, _ in word_counts.most_common(limit * 2):
        if word not in existing_tags and word not in new_tags:
            new_tags.append(word)
        if len(new_tags) >= limit:
            break
    return new_tags

# ========== メイン処理 ==========
def main():
    # 1. 既存タグを読み込む
    existing_tags = load_existing_tags()
    print(f"既存タグ数: {len(existing_tags)}")

    # 候補タグリスト = 既存タグ + デフォルトタグ（重複除去）
    candidate_tags = list(set(existing_tags) | set(DEFAULT_CANDIDATE_TAGS))
    print(f"分類候補タグ数: {len(candidate_tags)}")

    # 2. 最新のGistを取得
    res = requests.get(f"https://api.github.com/users/{USER}/gists?per_page=1")
    if not res.ok or not res.json():
        print("Gistが見つかりませんでした。")
        sys.exit(0)

    gist = res.json()[0]
    gist_id = gist['id']
    created_at = gist['created_at']
    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

    filename = dt.strftime("%Y年%m月%d日.md")
    filepath = os.path.join(POSTS_DIR, filename)

    if os.path.exists(filepath):
        print(f"スキップ: {filename} は既に存在します。")
        sys.exit(0)

    # 3. 内容を取得
    first_file_name = list(gist['files'].keys())[0]
    raw_url = gist['files'][first_file_name]['raw_url']
    content = requests.get(raw_url).text

    # 4. GLiClass で分類
    selected_tags = classify_tags(content, candidate_tags)
    print(f"GLiClass による選択タグ: {selected_tags}")

    # 5. コードブロックがあったら強制的に `code` を追加
    if has_code_block(content):
        if "code" not in selected_tags:
            selected_tags.append("code")
            print("コードブロックを検出したので 'code' タグを追加しました。")

    # 6. もし selected_tags が空の場合のフォールバック
    if not selected_tags:
        # 一番一般的と思われるタグを手動で追加（既存にあれば）
        fallback = ["gist"]
        if "gist" in candidate_tags:
            selected_tags = ["gist"]
        else:
            selected_tags = ["gist"]
        print(f"分類結果が空だったため、フォールバックタグ: {selected_tags}")

    # 7. 非テック判定（GLiClass で非テックタグが選ばれているか、またはルールベースで）
    non_tech_selected = any(tag in NON_TECH_TAGS for tag in selected_tags)
    if is_non_tech_content(content) or non_tech_selected:
        # 既存タグにない新タグを最大2個生成（ただし、非テックカテゴリの補完として）
        new_tags = generate_new_tags_from_content(content, existing_tags, limit=2)
        if new_tags:
            # 新タグは selected_tags に追加、ただし多くなりすぎないように
            for nt in new_tags:
                if nt not in selected_tags:
                    selected_tags.append(nt)
            print(f"非テックと判定されたため、新タグを追加: {new_tags}")

    # 重複除去
    selected_tags = list(dict.fromkeys(selected_tags))

    # 概要
    summary = (gist['description'] or content.split('\n')[0][:100]).replace('"', '\\"')

    # 8. Hugo 用フロントマターを書き出し
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: \"{summary}\"\n")
        f.write(f"date: {created_at}\n")
        f.write(f"gist_id: \"{gist_id}\"\n")
        f.write(f"tags: {selected_tags}\n")
        f.write("draft: false\n")
        f.write("---\n\n")
        f.write(content)

    print(f"完了！タグ {selected_tags} を付けて保存しました: {filename}")

if __name__ == "__main__":
    main()
