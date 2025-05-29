# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import spacy
from collections import Counter
import os

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

IGNORED_TOKENS = {"(", ")", ",", ".", ":", ";"}
POS_TAGS = [
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART",
    "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"
]
ENT_LABELS = [
    "PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART",
    "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"
]

@app.route("/", methods=["GET", "POST"])
def index():
    result, patterns = [], []

    text = ""
    target = ""

    if request.method == "POST":
        # --- Get text corpus ---
        text = request.form.get("text", "").strip()
        if not text and "file" in request.files:
            file = request.files["file"]
            if file and file.filename.endswith(".txt"):
                try:
                    text = file.read().decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        file.seek(0)
                        text = file.read().decode("shift_jis")
                    except UnicodeDecodeError:
                        text = "Error: Unable to decode corpus file."

        # --- Get target word ---
        target = request.form.get("target", "").strip()
        if not target and "target_file" in request.files:
            target_file = request.files["target_file"]
            if target_file and target_file.filename.endswith(".txt"):
                try:
                    target = target_file.read().decode("utf-8").strip()
                except UnicodeDecodeError:
                    try:
                        target_file.seek(0)
                        target = target_file.read().decode("shift_jis").strip()
                    except UnicodeDecodeError:
                        target = "ERROR_TARGET_DECODE"

        # --- Other parameters ---
        window   = int(request.form.get("window", 5))
        s_type   = request.form.get("search_type", "token")
        s_mode   = request.form.get("sort_mode", "sequential")

        doc = nlp(text.replace("\n", " "))
        matches = []

        if s_type == "token":
            tgt_doc    = nlp(target)
            tgt_texts  = [t.text.lower() for t in tgt_doc]
            span_len   = len(tgt_texts)

            for i in range(len(doc) - span_len + 1):
                ok = True
                for j in range(span_len):
                    tok     = doc[i + j]
                    t_lower = tok.text.lower()
                    tgt_txt = tgt_texts[j]

                    if t_lower != tgt_txt:
                        ok = False
                        break
                if ok and doc[i].text not in IGNORED_TOKENS:
                    matches.append((i, span_len))

        elif s_type == "pos":
            for i, tok in enumerate(doc):
                if tok.pos_ == target and tok.text not in IGNORED_TOKENS:
                    matches.append((i, 1))

        elif s_type == "entity":
            for ent in doc.ents:
                if ent.label_ == target.upper() and doc[ent.start].text not in IGNORED_TOKENS:
                    matches.append((ent.start, ent.end - ent.start))

        pattern_counter, output = Counter(), []
        for idx, span_len in matches:
            sent = next(s for s in doc.sents if s.start <= idx < s.end)
            loc  = idx - sent.start
            sent_tokens = [t.text for t in sent]

            left  = sent_tokens[max(0, loc - window): loc]
            mid   = sent_tokens[loc: loc + span_len]
            right = sent_tokens[loc + span_len: loc + span_len + window]

            next_tok = sent[loc + span_len] if (loc + span_len) < len(sent) else None
            if next_tok:
                pattern_counter[(next_tok.text, next_tok.pos_, next_tok.ent_type_ or "")] += 1

            output.append({
                "left": " ".join(left),
                "mid":  " ".join(mid),
                "right":" ".join(right),
                "next_word": next_tok.text.lower() if next_tok else "",
                "next_pos":  next_tok.pos_       if next_tok else ""
            })

        if s_mode == "token_freq":
            freq = Counter(o["next_word"] for o in output if o["next_word"])
            output.sort(key=lambda x: (-freq.get(x["next_word"], 0), x["left"], x["right"]))
        elif s_mode == "pos_freq":
            pos_freq = Counter(o["next_pos"] for o in output if o["next_pos"])
            output.sort(key=lambda x: (-pos_freq.get(x["next_pos"], 0), x["left"], x["right"]))

        result = output
        patterns = pattern_counter.most_common(10)

    return render_template(
        "index.html",
        result=result,
        patterns=patterns,
        pos_tags=POS_TAGS,
        ent_labels=ENT_LABELS
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))