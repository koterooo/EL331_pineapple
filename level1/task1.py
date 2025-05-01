#All parts of this code is written by ChatGPT

import re
from termcolor import colored

def kwic(text, target_ngram, window=5):
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Tokenize into words and punctuation
    tokens = re.findall(r'\w+|[^\w\s]', text)

    # Merge word + punctuation if directly attached (e.g., "data" + "." → "data.")
    merged_tokens = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and re.match(r'[.,;:!?]', tokens[i + 1]):
            merged_tokens.append(tokens[i] + tokens[i + 1])
            i += 2
        else:
            merged_tokens.append(tokens[i])
            i += 1

    # Split target n-gram for comparison
    target_words = target_ngram.split()
    n = len(target_words)

    for idx in range(len(merged_tokens) - n + 1):
        window_ngram = merged_tokens[idx:idx + n]

        # Remove trailing punctuation for comparison
        normalized_ngram = [re.sub(r'[.,;:!?]+$', '', w) for w in window_ngram]
        ngram_str = ' '.join(normalized_ngram)

        if ngram_str.lower() == target_ngram.lower():
            left = merged_tokens[max(0, idx - window):idx]
            right = merged_tokens[idx + n:idx + n + window]

            # Extract attached punctuation from the last word
            last_word = window_ngram[-1]
            match = re.match(r'(\w+)([.,;:!?]*)$', last_word)
            if match:
                main_part, punctuation = match.groups()
                window_ngram[-1] = main_part  # remove punctuation for highlighting

            # Highlight the keyword only
            colored_keyword = colored(' '.join(window_ngram), 'cyan', attrs=['bold'])

            # Add punctuation back after highlighting
            print(' '.join(left) + ' ' + colored_keyword + punctuation + ' ' + ' '.join(right))

# test usage
text = """
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
"""

s = input()
kwic(text, s)
