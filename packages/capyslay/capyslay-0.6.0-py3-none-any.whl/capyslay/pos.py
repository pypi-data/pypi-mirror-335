def pos():
    return [
        """
        import nltk
        from nltk.tokenize import word_tokenize

        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        """,
        """
        def pos_tagging(sentence):
            words = word_tokenize(sentence)
            tagged_words = nltk.pos_tag(words)
            return tagged_words
        """,
        """
        sentence = "The quick brown fox jumps over the lazy dog."
        tagged_sentence = pos_tagging(sentence)
        print(tagged_sentence)
        """
    ]