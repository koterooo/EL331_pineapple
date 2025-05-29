# -*- coding: utf-8 -*-
"""
Flask Application for Keyword‑in‑Context (KWIC) Text Analysis
============================================================
This source file was generated with the help of **ChatGPT (OpenAI)** on **29 May 2025**.

The app demonstrates how to:
  • Accept a body of text and perform keyword/POS/entity searches.
  • Extract KWIC windows and compute the most‑frequent next‑token patterns.
  • Provide three sorting modes (sequential, next‑token frequency, next‑POS frequency).

It is intentionally concise for educational purposes—feel free to extend it!
"""

from flask import Flask, render_template, request
import spacy
from collections import Counter
from difflib import SequenceMatcher

app = Flask(__name__)
# ---------------------------------------------------------------------------
# Load a lightweight English model from spaCy. This keeps container size small
# while still giving us tokenisation, POS tagging and named‑entity recognition.
# ---------------------------------------------------------------------------
nlp = spacy.load("en_core_web_sm")

# Characters that should never be treated as a valid keyword start token.
IGNORED_TOKENS = {"(", ")", ",", ".", ":", ";"}

# Static option lists for the drop‑down menus in the UI.
POS_TAGS = [
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART",
    "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"
]
ENT_LABELS = [
    "PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART",
    "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"
]

# ---------------------------------------------------------------------------
# Helper: fuzzy_eq
# Returns True if two strings are similar enough (Levenshtein ratio ≥ thresh).
# This lets us match minor misspellings such as "banane" → "banana".
# ---------------------------------------------------------------------------
def fuzzy_eq(a: str, b: str, thresh: float = 0.85) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= thresh

# ---------------------------------------------------------------------------
# Flask view: index()
# Handles GET (initial form) and POST (search request) at "/".
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result, patterns = [], []  # data for the template

    if request.method == "POST":
        # 1) Fetch form values ------------------------------------------------
        text     = request.form["text"]               # corpus
        target   = request.form["target"]             # search token / tag / label
        window   = int(request.form.get("window", 5)) # KWIC window size
        s_type   = request.form["search_type"]        # token / pos / entity
        s_mode   = request.form["sort_mode"]          # sequential / token_freq / pos_freq

        # 2) spaCy processing -------------------------------------------------
        doc = nlp(text.replace("\n", " "))  # flatten newlines for cleaner KWIC indices
        matches = []                            # [(start_idx, span_len), ...]

        # 3) Locate matches based on search type -----------------------------
        if s_type == "token":
            # --- Token search: exact, lemma and fuzzy match -----------------
            tgt_doc    = nlp(target)
            tgt_texts  = [t.text.lower()  for t in tgt_doc]
            tgt_lemmas = [t.lemma_.lower() for t in tgt_doc]
            span_len   = len(tgt_texts)

            for i in range(len(doc) - span_len + 1):
                ok = True
                for j in range(span_len):
                    tok       = doc[i + j]
                    t_lower   = tok.text.lower()
                    l_lower   = tok.lemma_.lower()
                    tgt_txt   = tgt_texts[j]
                    tgt_lem   = tgt_lemmas[j]

                    # Accept if token matches text/lemma or is fuzzily similar.
                    if not (
                        t_lower == tgt_txt or l_lower == tgt_txt or
                        t_lower == tgt_lem or l_lower == tgt_lem or
                        fuzzy_eq(t_lower, tgt_txt) or fuzzy_eq(l_lower, tgt_txt)
                    ):
                        ok = False
                        break
                if ok and doc[i].text not in IGNORED_TOKENS:
                    matches.append((i, span_len))

        elif s_type == "pos":
            # --- POS search --------------------------------------------------
            for i, tok in enumerate(doc):
                if tok.pos_ == target and tok.text not in IGNORED_TOKENS:
                    matches.append((i, 1))

        elif s_type == "entity":
            # --- Entity search ----------------------------------------------
            for ent in doc.ents:
                if ent.label_ == target.upper() and doc[ent.start].text not in IGNORED_TOKENS:
                    matches.append((ent.start, ent.end - ent.start))

        # 4) Build KWIC lines & collect next‑token statistics ----------------
        pattern_counter, output = Counter(), []
        for idx, span_len in matches:
            # Identify the sentence containing the match for pretty KWIC slicing.
            sent = next(s for s in doc.sents if s.start <= idx < s.end)
            loc  = idx - sent.start  # position within sentence
            sent_tokens = [t.text for t in sent]

            left  = sent_tokens[max(0, loc - window): loc]
            mid   = sent_tokens[loc: loc + span_len]
            right = sent_tokens[loc + span_len: loc + span_len + window]

            # Collect the word / POS immediately after the keyword span.
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

        # 5) Sort lines according to the requested mode ----------------------
        if s_mode == "token_freq":
            freq = Counter(o["next_word"] for o in output if o["next_word"])
            output.sort(key=lambda x: (-freq.get(x["next_word"], 0), x["left"], x["right"]))
        elif s_mode == "pos_freq":
            pos_freq = Counter(o["next_pos"] for o in output if o["next_pos"])
            output.sort(key=lambda x: (-pos_freq.get(x["next_pos"], 0), x["left"], x["right"]))
        # sequential = original document order → no extra sorting needed.

        result   = output
        patterns = pattern_counter.most_common(10)

    # 6) Render result page ---------------------------------------------------
    return render_template(
        "index.html",
        result=result,
        patterns=patterns,
        pos_tags=POS_TAGS,
        ent_labels=ENT_LABELS
    )

# ---------------------------------------------------------------------------
# Run the dev server (use a production WSGI server for real deployments).
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))