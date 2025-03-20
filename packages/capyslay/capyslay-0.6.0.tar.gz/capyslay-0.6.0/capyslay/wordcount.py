def wordcount():
    return [
        """
        import nltk
        from nltk.tokenize import word_tokenize
        from collections import Counter

        nltk.download('punkt')
        """,
        """
        def analyze_sentence(sentence, top_n):
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word.isalnum()]
            word_counts = Counter(words)
            print("Word Counts:")
            for word, count in word_counts.items():
                print(f"{word}: {count}")
            print("\nTop", top_n, "words:")
            for word, count in word_counts.most_common(top_n):
                print(f"{word}: {count}")
        """,
        """
        sentence = "The quick brown fox jumps over the lazy dog. The fox is quick."
        top_n = 3
        analyze_sentence(sentence, top_n)
        """
    ]
