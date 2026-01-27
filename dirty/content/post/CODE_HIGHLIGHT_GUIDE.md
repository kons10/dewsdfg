---
title: Hugoコードハイライトの使い方
date: 2026-01-28
---


## 設定完了！

`hugo.toml`と`style.css`を更新したから、コードハイライトが使えるようになったよ。

## 使い方

マークダウンファイルでコードブロックを書くときは、バッククォート3つ（```）を使って、言語名を指定するだけ。

### 例1: JavaScript

\```javascript
const greeting = "こんにちは！";
console.log(greeting);

function add(a, b) {
  return a + b;
}
\```

### 例2: Python

\```python
def greet(name):
    return f"こんにちは、{name}さん！"

print(greet("汐"))
\```

### 例3: HTML

\```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>サンプル</title>
</head>
<body>
    <h1>Hello World!</h1>
</body>
</html>
\```

### 例4: CSS

\```css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f0f0;
}
\```

## 対応している言語

Hugoは以下のような言語に対応してるよ：

- JavaScript / TypeScript
- Python
- Go
- HTML / CSS
- Java / Kotlin
- Rust
- Ruby
- PHP
- Shell / Bash
- JSON / YAML / TOML
- その他多数！

言語名を指定しなくても`guessSyntax = true`のおかげで自動判別してくれる。

## カスタマイズ方法

### スタイルを変更したい場合

`hugo.toml`の`style`パラメータを変更すれば、別のテーマが使えるよ：

```toml
[markup.highlight]
  style = "dracula"  # または github, vs, gruvbox など
```

利用可能なスタイルはHugoの公式ドキュメントで確認できる。

### 行番号を表示したい場合

```toml
[markup.highlight]
  lineNos = true
  lineNumbersInTable = true
```

これで行番号が表示されるようになる。`lineNumbersInTable = true`にするとコピペしやすくなるよ。

## トラブルシューティング

### コードハイライトが効かない場合

1. `hugo.toml`が正しく配置されているか確認（プロジェクトルートに配置）
2. `style.css`が`static/css/`ディレクトリに配置されているか確認
3. Hugoを再起動してみる：`hugo server --disableFastRender`

### 色がおかしい場合

`noClasses = false`になっているか確認。これがtrueだとインラインスタイルが使われて、CSSが無視される。

それじゃ、楽しいコーディングライフを！
