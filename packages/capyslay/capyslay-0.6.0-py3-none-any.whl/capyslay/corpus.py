def corpus():
    return [
        """
        import nltk
        from nltk.tokenize import word_tokenize
        nltk.download('punkt', quiet=True)
        """,
        """
        dummy_corpus = [
            "This is the first document.",
            "This document is the second document.",
            "And this is the third one.",
            "Is this the first document?",
            "This is another document."
        ]
        """,
        """
        def analyze_corpus(corpus):
            corpus_words = []
            for document in corpus:
                words = word_tokenize(document.lower())
                words = [word for word in words if word.isalnum()]
                corpus_words.extend(words)
            vocabulary = sorted(set(corpus_words))
            print("Corpus Words:")
            print(corpus_words)
            print("\nVocabulary:")
            print(vocabulary)
        """,
        """
        analyze_corpus(dummy_corpus)
        """
    ]