def grams():
    return [
        """
        import nltk
        from nltk.util import ngrams
        from nltk.tokenize import word_tokenize
        from collections import Counter
        """,
        """
        corpus = [
            "I skipped my breakfast today",
            "I ate my breakfast today",
            "I ate my lunch yesterday",
            "I skipped my lunch today"
        ]
        """,
        """
        tokenized_corpus = []
        for sentence in corpus:
            var = sentence.lower()
            var = word_tokenize(sentence)
            tokenized_corpus.append(var)
        """,
        """
        corpus_words = []
        for i in tokenized_corpus:
            for word in i:
                corpus_words.append(word)
        """,
        """
        vocab = set(corpus_words)
        """,
        """
        def grams(n):
            result = []
            for i in range(len(corpus_words)-n+1):
                result.append(tuple(corpus_words[i:i+n]))
            return result
        """,
        """
        print(grams(1))
        """,
        """
        print(grams(2))
        """,
        """
        print(grams(3))
        """
    ]