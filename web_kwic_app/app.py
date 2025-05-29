# -*- coding: utf-8 -*-
"""
KWIC Web App – Flask back-end
Last updated : 29 May 2025
Features
  • Exact-match token search
  • Lemma-based search (new)
  • POS / Entity search
  • .txt corpus upload (UTF-8 / Shift_JIS)
  • Loading indicator on the front-end
"""

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
    "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY",
    "ORDINAL", "CARDINAL"
]

# --------------------------------------------------------------------------- #
# Main view                                                                   #
# --------------------------------------------------------------------------- #
@app.route("/", methods=["GET", "POST"])
def index():
    result, patterns = [], []

    if request.method == "POST":
        # --- 1.  Corpus text (textarea OR file) ---------------------------- #
        text = request.form.get("text", "").strip()
        if not text and "file" in request.files:
            file = request.files["file"]
            if file and file.filename.endswith(".txt"):
                for enc in ("utf-8", "shift_jis"):
                    try:
                        file.seek(0)
                        text = file.read().decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                if not text:
                    text = "Error: Unable to decode file. Use UTF-8 or Shift_JIS."

        # --- 2.  Search parameters ---------------------------------------- #
        target   = request.form.get("target", "").strip()
        s_type   = request.form.get("search_type", "token")   # token / lemma / pos / entity
        window   = int(request.form.get("window", 5))
        s_mode   = request.form.get("sort_mode", "sequential")

        # --- 3.  spaCy processing ----------------------------------------- #
        doc = nlp(text.replace("\n", " "))
        matches = []  # list[(idx, span_len)]

        # --- 3-A  Token search (exact) ------------------------------------ #
        if s_type == "token":
            tgt_doc   = nlp(target)
            tgt_txts  = [t.text.lower() for t in tgt_doc]
            span_len  = len(tgt_txts)

            for i in range(len(doc) - span_len + 1):
                ok = True
                for j in range(span_len):
                    if doc[i + j].text.lower() != tgt_txts[j]:
                        ok = False
                        break
                if ok and doc[i].text not in IGNORED_TOKENS:
                    matches.append((i, span_len))

        # --- 3-B  Lemma search (new) -------------------------------------- #
        elif s_type == "lemma":
            tgt_doc   = nlp(target)
            tgt_lems  = [t.lemma_.lower() for t in tgt_doc]
            span_len  = len(tgt_lems)

            for i in range(len(doc) - span_len + 1):
                ok = True
                for j in range(span_len):
                    if doc[i + j].lemma_.lower() != tgt_lems[j]:
                        ok = False
                        break
                if ok and doc[i].text not in IGNORED_TOKENS:
                    matches.append((i, span_len))

        # --- 3-C  POS search --------------------------------------------- #
        elif s_type == "pos":
            for i, tok in enumerate(doc):
                if tok.pos_ == target and tok.text not in IGNORED_TOKENS:
                    matches.append((i, 1))

        # --- 3-D  Entity search ------------------------------------------ #
        elif s_type == "entity":
            for ent in doc.ents:
                if ent.label_ == target.upper() and doc[ent.start].text not in IGNORED_TOKENS:
                    matches.append((ent.start, ent.end - ent.start))

        # --- 4.  Build KWIC lines & stats --------------------------------- #
        pattern_counter, output = Counter(), []
        for idx, span_len in matches:
            sent = next(s for s in doc.sents if s.start <= idx < s.end)
            loc  = idx - sent.start
            toks = [t.text for t in sent]

            left  = toks[max(0, loc - window): loc]
            mid   = toks[loc: loc + span_len]
            right = toks[loc + span_len: loc + span_len + window]

            next_tok = sent[loc + span_len] if (loc + span_len) < len(sent) else None
            if next_tok:
                pattern_counter[(next_tok.text, next_tok.pos_, next_tok.ent_type_ or "")] += 1

            output.append({
                "left":  " ".join(left),
                "mid":   " ".join(mid),
                "right": " ".join(right),
                "next_word": next_tok.text.lower() if next_tok else "",
                "next_pos":  next_tok.pos_       if next_tok else ""
            })

        # --- 5.  Sort ------------------------------------------------------ #
        if s_mode == "token_freq":
            freq = Counter(o["next_word"] for o in output if o["next_word"])
            output.sort(key=lambda x: (-freq.get(x["next_word"], 0), x["left"], x["right"]))
        elif s_mode == "pos_freq":
            pfreq = Counter(o["next_pos"] for o in output if o["next_pos"])
            output.sort(key=lambda x: (-pfreq.get(x["next_pos"], 0), x["left"], x["right"]))

        result   = output
        patterns = pattern_counter.most_common(10)

    # --- 6.  Render ------------------------------------------------------- #
    return render_template(
        "index.html",
        result=result,
        patterns=patterns,
        pos_tags=POS_TAGS,
        ent_labels=ENT_LABELS
    )

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))