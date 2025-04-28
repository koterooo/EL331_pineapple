def extract_centered_context_html_with_css_fixed(sentence, keyword, window=5):
    words = sentence.split()
    results = []

    for i, word in enumerate(words):
        stripped_word = word.strip('.,!?()[]{}"\'')
        if stripped_word.lower() == keyword.lower():
            start = max(i - window, 0)
            end = min(i + window + 1, len(words))

            # 前後の語を取得
            pre_words = words[start:i]
            post_words = words[i+1:end]

            # パディング（不足を空文字で）
            pad_pre = [""] * (window - len(pre_words))
            pad_post = [""] * (window - len(post_words))

            # タグ構造
            pre_html = ' '.join(pad_pre + pre_words)
            post_html = ' '.join(post_words + pad_post)
            ai_html = f'<span class="ai">{words[i]}</span>'

            html_line = (
                f'<div class="context-line">'
                f'<span class="pre">{pre_html}</span>'
                f'{ai_html}'
                f'<span class="post">{post_html}</span>'
                f'</div>'
            )
            results.append(html_line)

    return results


# 最終HTML構築
def build_final_html(sentences, keyword):
    all_contexts = []
    for sentence in sentences:
        contexts = extract_centered_context_html_with_css_fixed(sentence, keyword)
        if contexts:
            all_contexts.extend(contexts)

    if not all_contexts:
        return "AI を含む文は見つかりませんでした。"

    html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset='UTF-8'>
  <title>AI検索結果</title>
  <style>
    body { font-family: monospace; background: #fff; }
    .context-line {
      width: 100%;
      display: flex;
      justify-content: center;
      font-family: monospace;
      white-space: pre;
      margin-bottom: 8px;
    }
    .ai {
      color: red;
      font-weight: bold;
      min-width: 4ch;
      text-align: center;
      padding: 0 1ch;
    }
    .pre, .post {
      display: inline-block;
      min-width: 25ch;
      text-align: right;
      padding: 0 1ch;
    }
    .post {
      text-align: left;
    }
  </style>
</head>
<body>
<h2 style='text-align:center;'>🔍 AI を中央にした文脈（前後5単語、不足は空白で調整）</h2>
"""
    html += "\n".join(all_contexts)
    html += "\n</body></html>"
    return html


# サンプル文リスト
sample_texts = [
    "AI is transforming industries rapidly.",
    "Artificial intelligence is changing the way we live and work.",
    "AI is now being used to detect diseases earlier and with greater accuracy.",
    "Self-driving vehicles rely heavily on AI to navigate safely.",
    "AI research.",
    "The forest was peaceful and quiet.",
    "She enjoys painting landscapes during the weekend.",
    "AI.",
    "The role of AI in education is growing.",
    "He climbed the snowy peak alone."
]

keyword = "AI"
final_html = build_final_html(sample_texts, keyword)

# ① ファイルに保存
with open("output.html", "w", encoding="utf-8") as f:
    f.write(final_html)

# ② ブラウザで自動オープン
import webbrowser
webbrowser.open("output.html")