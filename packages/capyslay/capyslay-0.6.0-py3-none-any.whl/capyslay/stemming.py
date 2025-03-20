def stemming():
    return [
        """
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.stem import PorterStemmer

        nltk.download('punkt', quiet=True)
        """,
        """
        def stemming_corpus(corpus):
            stemmer = PorterStemmer()
            stemmed_corpus = []

            for document in corpus:
                words = word_tokenize(document.lower())
                stemmed_words = [stemmer.stem(word) for word in words if word.isalnum()]
                stemmed_corpus.append(" ".join(stemmed_words))

            return stemmed_corpus
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
        stemmed_corpus = stemming_corpus(dummy_corpus)
        print(stemmed_corpus)
        """
    ]