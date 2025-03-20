def smoothing():
    return [
        """
        import nltk
        from collections import Counter
        from nltk.tokenize import word_tokenize
        """,
        """
        nltk.download('punkt')
        """,
        """
        corpus = [
            'the', 'cat', 'sat', 'on', 'the', 'mat',
            'the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog'
        ]

        v = Counter(corpus)
        n = sum(v.values())

        print(f"Word count: \n{v}")
        print(f"Total count: {n}")
        """,
        """
        vocab = len(v)
        total_vocab = vocab+n   
        """,
        """
        # laplace smoothing

        probs = {}
        for word, count in v.items():
            probs[word] = (count + 1) / n

        print("\nProbabilities:")
        for key, value in probs.items():
            print(f"{key}, {round(value, 4)}")  
        """,
        """
        # Add-k Smoothing

        k=0.5
        additive_probs = {}
        for word, count in v.items():
            var = (count + k) / (n + k * vocab)
            additive_probs[word] = var

        print("\nProbabilities: ")
        for key, value in additive_probs.items():
            print(f"{key}, {round(value, 4)}")        
        """,
        """
        # preparing the data
        tokenized_corpus = []
        for sentence in corpus:
            var = sentence.lower()
            var = word_tokenize(sentence)
            tokenized_corpus.append(var)

        corpus_words = []
        for i in tokenized_corpus:
            for word in i:
                corpus_words.append(word)
            
        vocab = set(corpus_words)
        def grams(n):
            result = []
            for i in range(len(corpus_words)-n+1):
                result.append(tuple(corpus_words[i:i+n]))
            return result
        """,
        """
        unigram = grams(1)
        unigram_counter = Counter(unigram)
        bigrams = grams(2)
        bigrams_counter = Counter(bigrams)
        """,
        """
        unigram_prob = {unigram: count / n for unigram, count in unigram_counter.items()}
        bigram_prob = {bigram: count / n for bigram, count in bigrams_counter.items()}
        """,
        """
        # Interpolated smoothing

        l1 = 0.7
        l2 = 0.3

        interpolated_prob = {}
        for (w1, w2), count in bigrams_counter.items():
            bigram_p = bigram_prob.get((w1, w2), 0)
            unigram_p = unigram_prob.get(w2, 0)
            
            interpolated_prob[(w1, w2)] = l1 * bigram_p + l2 * unigram_p

        for key, value in interpolated_prob.items():
            print(f"{key}, {round(value, 4)}")
        """
    ]