import re
from termcolor import colored
import spacy

nlp = spacy.load('en_core_web_sm')

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
        raise ValueError("search_type must be one of: 'token', 'pos', 'entity'")

    for idx, length in matches:
        # Find the sentence that contains the match
        for sent in doc.sents:
            if sent.start <= idx < sent.end:
                sent_tokens = [tok.text_with_ws for tok in sent]
                local_idx = idx - sent.start
                left = sent_tokens[max(0, local_idx - window): local_idx]
                mid = sent_tokens[local_idx: local_idx + length]
                right = sent_tokens[local_idx + length: local_idx + length + window]
                mid_str = ''.join(mid).strip()
                highlighted = colored(mid_str, color, attrs=attrs)
                print(''.join(left).strip() + ' ' + highlighted + ' ' + ''.join(right).strip())
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

    # Prompt user for search mode first
    st = input("Select search mode (token / pos / entity, default is token): ").strip().lower()
    search_type = st if st in {'token', 'pos', 'entity'} else 'token'

    # Show valid options depending on search mode
    if search_type == 'pos':
        print("Available POS tags: NOUN, VERB, ADJ, ADV, PROPN, DET, ADP, AUX")
    elif search_type == 'entity':
        print("Available entity labels: PERSON, ORG, GPE, DATE, MONEY, TIME")

    # Prompt for the target keyword or pattern
    target = input(f"Enter target for {search_type} search: ")

    w_in = input("Enter window size (number of words left/right, default is 5): ").strip()
    window = int(w_in) if w_in.isdigit() and int(w_in) > 0 else 5

    color_in = input("Enter highlight color (grey, red, green, yellow, blue, magenta, cyan, white; default is cyan): ").strip().lower()
    colors = {'grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'}
    color = color_in if color_in in colors else 'cyan'

    attrs_in = input("Enter attributes (comma-separated: bold, underline, blink, reverse, concealed; default is bold): ").strip().lower()
    valid_attrs = {'bold', 'underline', 'blink', 'reverse', 'concealed'}
    if attrs_in:
        attrs = [a.strip() for a in attrs_in.split(',') if a.strip() in valid_attrs]
        attrs = attrs or ['bold']
    else:
        attrs = ['bold']

    print(f"\n=== KWIC (mode={search_type}, window={window}, color={color}, attrs={attrs}) ===\n")
    kwic(text, target, window=window, search_type=search_type, color=color, attrs=attrs)