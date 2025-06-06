import re
from termcolor import colored
import spacy
from spacy.cli import download as spacy_download

def load_spacy_model(name: str):
    try:
        return spacy.load(name)
    except OSError:
        print(f"モデル '{name}' が見つかりません。ダウンロード中…")
        spacy_download(name)
        print(f"モデル '{name}' ダウンロード完了。")
        return spacy.load(name)

nlp = load_spacy_model('en_core_web_sm')

def kwic(text, target, window=5, search_type='token', color='cyan', attrs=None):
    if attrs is None:
        attrs = ['bold']

    doc = nlp(text)
    tokens = [tok.text for tok in doc]
    matches = []

    if search_type == 'token':
        target_words = target.split()
        n = len(target_words)
        lowered = [t.lower() for t in tokens]
        for i in range(len(tokens) - n + 1):
            if lowered[i:i+n] == [w.lower() for w in target_words]:
                matches.append((i, n))

    elif search_type == 'pos':
        target_tags = target.split()
        n = len(target_tags)
        pos_list = [tok.pos_ for tok in doc]
        for i in range(len(pos_list) - n + 1):
            if pos_list[i:i+n] == target_tags:
                matches.append((i, n))

    elif search_type == 'entity':
        ent_type = target.upper()
        for ent in doc.ents:
            if ent.label_ == ent_type:
                matches.append((ent.start, ent.end - ent.start))

    else:
        raise ValueError("search_type は 'token','pos','entity' のいずれかを指定してください。")

    for idx, length in matches:
        # 所属する文を特定
        for sent in doc.sents:
            if sent.start <= idx < sent.end:
                sent_tokens = [tok.text for tok in sent]
                local_idx = idx - sent.start
                left = sent_tokens[max(0, local_idx - window): local_idx]
                mid = sent_tokens[local_idx: local_idx + length]
                right = sent_tokens[local_idx + length: local_idx + length + window]
                mid_str = ' '.join(mid)
                highlighted = colored(mid_str, color, attrs=attrs)
                print(' '.join(left) + ' ' + highlighted + ' ' + ' '.join(right))
                break

if __name__ == '__main__':
    text = """
    Natural language processing (NLP) has undergone significant transformation over the past few decades.
    Techniques have evolved from simple rule-based systems to sophisticated neural models,
    enabling tasks such as machine translation, sentiment analysis, and question answering.
    Language models like BERT, GPT, and RoBERTa have transformed the way machines understand text.
    With advancements in attention mechanisms and transformer architectures,
    these systems achieve state-of-the-art results across multiple benchmarks.
    Researchers are now focusing on multilingual capabilities, model interpretability, and ethical considerations.
    Tools like spaCy and HuggingFace Transformers have democratized access to powerful NLP models.
    Applications include chatbots, summarization, translation, and sentiment detection.
    As computing power grows, so does the potential for real-time, context-aware NLP applications.
    However, issues such as bias, hallucination, and data privacy still pose challenges.
    The future of NLP lies in responsible innovation, interdisciplinary collaboration,
    and a deeper integration with human communication needs.
    Barack Obama was born in Hawaii and served as the 44th President of the United States.
    He delivered a keynote speech in New York City on climate change policy.
    The event was hosted by the United Nations and attended by representatives from Google and Microsoft.
    On January 1, 2020, the organization pledged $1,000,000 to support renewable energy projects.
    Meetings are scheduled daily at 10:00 AM in Geneva, Switzerland to evaluate the progress.
    """

    # 検索モードの入力を先に
    st = input("検索モードを選択してください （token / pos / entity、デフォルト token）：").strip().lower()
    search_type = st if st in {'token', 'pos', 'entity'} else 'token'

    # モードに合わせてターゲット語を入力
    if search_type == 'pos':
        print("利用可能な POS タグの例: NOUN, VERB, ADJ, ADV, PROPN, DET, ADP, AUX")
    elif search_type == 'entity':
        print("利用可能な固有表現ラベルの例: PERSON, ORG, GPE, DATE, MONEY, TIME")
    target = input(f"{search_type} モードで検索するターゲットを入力してください：")

    w_in = input("窓サイズを入力してください （左右に表示するトークン数、デフォルト5）：").strip()
    window = int(w_in) if w_in.isdigit() and int(w_in) > 0 else 5

    color_in = input("ハイライト色を入力してください （grey, red, green, yellow, blue, magenta, cyan, white、デフォルト cyan）：").strip().lower()
    colors = {'grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'}
    color = color_in if color_in in colors else 'cyan'

    attrs_in = input("属性を入力してください （comma 区切り、bold, underline, blink, reverse, concealed、デフォルト bold）：").strip().lower()
    valid_attrs = {'bold', 'underline', 'blink', 'reverse', 'concealed'}
    if attrs_in:
        attrs = [a.strip() for a in attrs_in.split(',') if a.strip() in valid_attrs]
        attrs = attrs or ['bold']
    else:
        attrs = ['bold']

    print(f"\n=== KWIC (mode={search_type}, window={window}, color={color}, attrs={attrs}) ===\n")
    kwic(text, target, window=window, search_type=search_type, color=color, attrs=attrs)
