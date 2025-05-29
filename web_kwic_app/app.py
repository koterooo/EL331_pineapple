from flask import Flask, render_template, request
import spacy
from collections import Counter

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

IGNORED_TOKENS = {"(", ")", ",", ".", ":", ";"}

POS_TAGS = [
    "ADJ","ADP","ADV","AUX","CCONJ","DET","INTJ","NOUN","NUM","PART",
    "PRON","PROPN","PUNCT","SCONJ","SYM","VERB","X"
]
ENT_LABELS = [
    "PERSON","NORP","FAC","ORG","GPE","LOC","PRODUCT","EVENT","WORK_OF_ART",
    "LAW","LANGUAGE","DATE","TIME","PERCENT","MONEY","QUANTITY","ORDINAL","CARDINAL"
]

@app.route("/", methods=["GET", "POST"])
def index():
    result, patterns = [], []

    if request.method == "POST":
        text     = request.form["text"]
        target   = request.form["target"]
        window   = int(request.form.get("window", 5))
        s_type   = request.form["search_type"]
        s_mode   = request.form["sort_mode"]

        doc     = nlp(text.replace("\n", " "))
        tokens  = [t.text for t in doc]
        matches = []

        # --- 検索 ---
        if s_type == "token":
            tgt_words = target.split()
            n = len(tgt_words)
            lowered = [t.lower() for t in tokens]
            for i in range(len(tokens) - n + 1):
                if lowered[i:i+n] == [w.lower() for w in tgt_words]:
                    if tokens[i] not in IGNORED_TOKENS:
                        matches.append((i, n))
        elif s_type == "pos":
            for i, tok in enumerate(doc):
                if tok.pos_ == target and tok.text not in IGNORED_TOKENS:
                    matches.append((i, 1))
        elif s_type == "entity":
            for ent in doc.ents:
                if ent.label_ == target.upper() and doc[ent.start].text not in IGNORED_TOKENS:
                    matches.append((ent.start, ent.end - ent.start))

        # --- KWIC & パターン集計 ---
        pattern_counter, output = Counter(), []
        for idx, length in matches:
            sent = next(s for s in doc.sents if s.start <= idx < s.end)
            loc  = idx - sent.start
            s_tok = [t.text for t in sent]
            left  = s_tok[max(0, loc - window): loc]
            mid   = s_tok[loc: loc + length]
            right = s_tok[loc + length: loc + length + window]

            nxt = sent[loc + length] if (loc + length) < len(sent) else None
            if nxt:
                pattern_counter[(nxt.text, nxt.pos_, nxt.ent_type_ or "")] += 1

            output.append({"left": " ".join(left),
                           "mid":  " ".join(mid),
                           "right":" ".join(right)})

        # --- 並べ替え ---
        if s_mode == "token_freq":
            freq = Counter(d["mid"] for d in output)
            output.sort(key=lambda x: -freq[x["mid"]])
        elif s_mode == "pos_freq":
            pos_freq = Counter(p[1] for p in pattern_counter)
            output.sort(key=lambda x: -pos_freq.get(x["mid"], 0))

        result   = output
        patterns = pattern_counter.most_common(10)

    return render_template(
        "index.html",
        result=result,
        patterns=patterns,
        pos_tags=POS_TAGS,        # ★ 追加
        ent_labels=ENT_LABELS     # ★ 追加
    )

if __name__ == "__main__":
    import os
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))