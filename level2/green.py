import re
from termcolor import colored as color_text
from collections import Counter
import spacy

nlp = spacy.load("en_core_web_sm")

def kwic(
    text: str,
    target: str,
    *,
    window: int = 5,
    search_type: str = "token",
    color: str = "cyan",
    attrs=None,
    display_mode: str = "sequential",
):
    """
    Parameters
    ----------
    text : str
        入力テキスト
    target : str
        検索語 / POS シーケンス / エンティティラベル
    window : int
        KWIC の左右語数
    search_type : {'token', 'pos', 'entity'}
        検索タイプ
    display_mode : {'sequential', 'token_freq', 'pos_freq'}
        表示順の決め方
    """
    if attrs is None:
        attrs = ["bold"]

    if display_mode not in {"sequential", "token_freq", "pos_freq"}:
        raise ValueError("display_mode must be sequential | token_freq | pos_freq")

    doc = nlp(text)
    lowered_tokens = [tok.text.lower() for tok in doc]
    pos_list = [tok.pos_ for tok in doc]

    # ---------- マッチ検出 ----------
    matches = []  # (start_idx, length) のタプル
    if search_type == "token":
        pattern = target.lower().split()
        n = len(pattern)
        for i in range(len(doc) - n + 1):
            if lowered_tokens[i : i + n] == pattern:
                matches.append((i, n))

    elif search_type == "pos":
        pattern = target.upper().split()
        n = len(pattern)
        for i in range(len(doc) - n + 1):
            if pos_list[i : i + n] == pattern:
                matches.append((i, n))

    elif search_type == "entity":
        label = target.upper()
        for ent in doc.ents:
            if ent.label_ == label:
                matches.append((ent.start, ent.end - ent.start))

    # ---------- KWIC 行を構築 ----------
    lines = []
    for idx, length in matches:
        sent = doc[idx].sent  # マッチを含むセンテンス
        local = idx - sent.start
        sent_tokens = [tok.text for tok in sent]

        left  = sent_tokens[max(0, local - window) : local]
        mid   = sent_tokens[local : local + length]
        right = sent_tokens[local + length : local + length + window]

        follow_idx = idx + length
        follow_tok = doc[follow_idx].text if follow_idx < len(doc) else ""
        follow_pos = doc[follow_idx].pos_ if follow_idx < len(doc) else ""

        lines.append(
            {
                "left": left,
                "mid": mid,
                "right": right,
                "follow_token": follow_tok,
                "follow_pos": follow_pos,
            }
        )

    # ---------- 並べ替え ----------
    if display_mode == "token_freq":
        freq = Counter(l["follow_token"].lower() for l in lines if l["follow_token"])
        lines.sort(
            key=lambda l: (-freq[l["follow_token"].lower()], l["follow_token"].lower())
        )
    elif display_mode == "pos_freq":
        freq = Counter(l["follow_pos"] for l in lines if l["follow_pos"])
        lines.sort(key=lambda l: (-freq[l["follow_pos"]], l["follow_pos"]))

    # ---------- 出力 ----------
    for l in lines:
        mid_str = " ".join(l["mid"])
        highlighted = color_text(mid_str, color, attrs=attrs)
        print(
            "{} {} {}".format(
                " ".join(l["left"]), highlighted, " ".join(l["right"])
            ).strip()
        )


if __name__ == "__main__":
    # --- 例示用テキスト ---
    TEXT = """
    Natural language processing (NLP) has undergone significant transformation over the past few decades. In the early stages, researchers focused primarily on rule-based approaches, developing complex sets of handcrafted linguistic rules to analyze and generate human language. These systems, while groundbreaking at the time, struggled with scalability and adaptability, often requiring extensive manual effort for even modest improvements.
The 1980s and 1990s saw the rise of statistical methods. With access to larger datasets and more powerful computing resources, researchers began employing probabilistic models to capture language patterns more effectively. Techniques such as Hidden Markov Models and n-gram language models became central to tasks like speech recognition, part-of-speech tagging, and machine translation. These models represented a significant improvement over purely rule-based systems, but they still faced challenges in handling long-range dependencies and understanding context deeply.
The advent of deep learning in the early 2010s marked a pivotal moment for NLP. Researchers started leveraging neural networks, particularly recurrent neural networks (RNNs) and later long short-term memory networks (LSTMs), to model sequences of text. These architectures were better suited for capturing temporal dependencies, leading to major advances in tasks such as sentiment analysis, machine translation, and question answering.
Perhaps the most transformative development came with the introduction of transformer architectures. The paper "Attention is All You Need," published in 2017, proposed a new model that relied entirely on self-attention mechanisms, dispensing with recurrence altogether. Transformers quickly became the foundation for a new generation of language models, including BERT (Bidirectional Encoder Representations from Transformers), GPT (Generative Pretrained Transformer), RoBERTa, T5, and many others. These models demonstrated unprecedented capabilities in understanding and generating human language.
Pretrained language models, in particular, revolutionized NLP workflows. By training on massive corpora of text and fine-tuning on specific tasks, these models enabled high performance across a wide range of applications with relatively modest amounts of task-specific data. Transfer learning became a standard practice, dramatically lowering the barrier to entry for developing high-quality NLP systems.
Today, NLP applications are ubiquitous. Virtual assistants like Siri, Alexa, and Google Assistant rely heavily on natural language understanding and generation. Machine translation systems, such as Google Translate and DeepL, offer near-human-level translations for many language pairs. Sentiment analysis tools are widely used by businesses to monitor public opinion, and automatic summarization systems help manage information overload by condensing lengthy documents into concise summaries.
Despite these advances, significant challenges remain. One major issue is bias in language models. Because these models learn from large datasets scraped from the internet, they often inherit and even amplify societal biases present in the data. Addressing this problem requires a combination of better data curation, improved training techniques, and more robust evaluation methods.
Another challenge is interpretability. Deep learning models, particularly large transformers, are often described as "black boxes" because it can be difficult to understand why they make particular predictions. Researchers are actively exploring methods for explaining model behavior, such as attention visualization, probing tasks, and influence functions.
Efficiency is also a critical concern. State-of-the-art language models require enormous computational resources to train and deploy, raising environmental and accessibility concerns. Techniques like model pruning, knowledge distillation, and efficient architecture design aim to mitigate these issues, making NLP systems more sustainable and inclusive.
The future of NLP looks extremely promising. One exciting direction is multimodal learning, where models are trained to process and generate not just text, but also images, audio, and video. Models like CLIP and DALL-E exemplify this trend, demonstrating impressive abilities to connect language with other modalities.
Another frontier is multilingual and low-resource language processing. While major languages like English, Chinese, and Spanish have received significant attention, many of the world's languages remain underserved. Developing models that can work effectively across diverse languages and dialects is a critical step toward more equitable AI systems.
Personalization and customization are also key trends. Future NLP systems are expected to adapt to individual users' preferences, communication styles, and needs. This requires advancements in user modeling, privacy-preserving learning, and human-AI interaction design.
In addition, there is a growing interest in grounding language models in real-world knowledge and experiences. Current models often generate plausible but incorrect information because they lack true understanding. Integrating language models with structured knowledge bases, retrieval systems, and sensory data could lead to more accurate and trustworthy AI systems.
Ethical considerations will play an increasingly important role in the development and deployment of NLP technologies. Issues such as data privacy, misinformation, digital manipulation, and the digital divide must be addressed thoughtfully and proactively. Researchers, policymakers, and industry leaders must collaborate to create frameworks and standards that ensure NLP technologies are developed and used responsibly.
Finally, education and public literacy about AI and NLP are crucial. As these technologies become more embedded in daily life, it is important for people to understand how they work, what their limitations are, and how to critically evaluate their outputs. Initiatives to democratize AI knowledge and tools will help foster a more informed and empowered society.
In conclusion, natural language processing has come a long way, evolving from simple rule-based systems to sophisticated transformer models capable of remarkable feats. While tremendous progress has been made, the journey is far from over. By addressing current challenges and pursuing ambitious new goals, the NLP community can continue to create technologies that enhance communication, foster understanding, and benefit humanity as a whole.
Looking ahead, we can expect NLP to become even more intertwined with our daily lives. Future systems may seamlessly assist with writing, translation, summarization, information retrieval, and creative endeavors, all while respecting user agency and promoting inclusivity. Collaboration between humans and AI will likely become more natural and intuitive, blurring the lines between tool and partner.
The journey toward truly intelligent and responsible NLP systems will require not just technical innovation, but also ethical foresight, interdisciplinary collaboration, and a commitment to serving the broader public good. By keeping these principles at the forefront, we can ensure that the future of natural language processing is bright, equitable, and inspiring for generations to come.
"""  # ここに長文を入れてください

    # --- CLI 入力 ---
    st = input("search mode (token / pos / entity) [token]: ").strip().lower() or "token"

    if st == "pos":
        print("POS tags 例: NOUN VERB PROPN ADJ ADV")
    elif st == "entity":
        print("ENTITY 例: PERSON ORG GPE DATE MONEY TIME")

    target = input(f"target for {st}: ").strip()
    window = int(input("window size [5]: ") or 5)
    color  = input("color [cyan]: ").strip().lower() or "cyan"
    attrs  = [a for a in (input("attrs (bold,underline,...) [bold]: ").split(",")) if a] or ["bold"]
    mode   = input("display (sequential / token_freq / pos_freq) [sequential]: ").strip() or "sequential"

    print("\n=== KWIC ===\n")
    kwic(
        TEXT,
        target,
        window=window,
        search_type=st,
        color=color,
        attrs=attrs,
        display_mode=mode,
    )
