from flask import Flask, render_template, request
import spacy
from collections import Counter

nlp = spacy.load('en_core_web_sm')
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    patterns = []

    if request.method == "POST":
        text = request.form["text"]
        target = request.form["target"]
        window = int(request.form.get("window", 5))
        search_type = request.form["search_type"]
        sort_mode = request.form["sort_mode"]

        doc = nlp(text.replace('\n', ' '))
        tokens = [tok.text for tok in doc]
        matches = []

        if search_type == "token":
            target_words = target.split()
            n = len(target_words)
            lowered = [t.lower() for t in tokens]
            for i in range(len(tokens) - n + 1):
                if lowered[i:i+n] == [w.lower() for w in target_words]:
                    matches.append((i, n))
        elif search_type == "pos":
            target_tags = target.split()
            n = len(target_tags)
            pos_list = [tok.pos_ for tok in doc]
            for i in range(len(pos_list) - n + 1):
                if pos_list[i:i+n] == target_tags:
                    matches.append((i, n))
        elif search_type == "entity":
            for ent in doc.ents:
                if ent.label_ == target.upper():
                    matches.append((ent.start, ent.end - ent.start))

        pattern_counter = Counter()
        output_data = []
        for idx, length in matches:
            for sent in doc.sents:
                if sent.start <= idx < sent.end:
                    local_idx = idx - sent.start
                    sent_tokens = [tok.text for tok in sent]
                    left = sent_tokens[max(0, local_idx - window): local_idx]
                    mid = sent_tokens[local_idx: local_idx + length]
                    right = sent_tokens[local_idx + length: local_idx + length + window]

                    next_tok = sent[local_idx + length] if (local_idx + length) < len(sent) else None
                    next_info = (next_tok.text, next_tok.pos_) if next_tok else ("", "")
                    pattern_counter[next_info] += 1

                    output_data.append({
                        "left": " ".join(left),
                        "mid": " ".join(mid),
                        "right": " ".join(right)
                    })
                    break

        if sort_mode == "token_freq":
            token_freq = Counter([d["mid"] for d in output_data])
            output_data.sort(key=lambda x: -token_freq[x["mid"]])
        elif sort_mode == "pos_freq":
            pos_freq = Counter([p[1] for p in pattern_counter])
            output_data.sort(key=lambda x: -pos_freq.get(x["mid"], 0))

        result = output_data
        patterns = pattern_counter.most_common(10)

    return render_template("index.html", result=result, patterns=patterns)

if __name__ == "__main__":
    app.run(debug=True)
