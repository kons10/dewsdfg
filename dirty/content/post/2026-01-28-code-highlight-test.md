---
title: "コードハイライトテスト"
date: 2026-01-28T15:30:00+09:00
tags: ["test", "code"]

---

今回の更新で、コードハイライトがHugoデフォルトで有効になりました！
コードハイライトがちゃんと動くかテストするよ！
<!--more-->

## JavaScriptのサンプル

```javascript
const greeting = "こんにちは！";
console.log(greeting);

function add(a, b) {
  return a + b;
}

const result = add(5, 3);
console.log(`5 + 3 = ${result}`);
```

## Pythonのサンプル

```python
def greet(name):
    return f"こんにちは、{name}さん！"

print(greet("汐"))

# リスト内包表記
squares = [x**2 for x in range(10)]
print(squares)
```

## HTMLのサンプル

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>サンプルページ</title>
</head>
<body>
    <h1>Hello World!</h1>
    <p>これはテストです。</p>
</body>
</html>
```

## CSSのサンプル

```css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f0f0;
  padding: 2rem;
}

.card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

## Goのサンプル

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, 汐!")
    
    result := add(5, 3)
    fmt.Printf("5 + 3 = %d\n", result)
}

func add(a, b int) int {
    return a + b
}
```

これで色がついてれば成功！
