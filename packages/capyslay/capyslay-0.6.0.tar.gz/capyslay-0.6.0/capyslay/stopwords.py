def stopwords():
    return [
        """
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords

        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        """,
        """
        def remove_stopwords(corpus):
            stop_words = set(stopwords.words('english'))
            filtered_corpus = []

            for document in corpus:
                words = word_tokenize(document.lower())
                filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
                filtered_corpus.append(" ".join(filtered_words))

            return filtered_corpus
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
        filtered_corpus = remove_stopwords(dummy_corpus)
        print(filtered_corpus)
        """
    ]