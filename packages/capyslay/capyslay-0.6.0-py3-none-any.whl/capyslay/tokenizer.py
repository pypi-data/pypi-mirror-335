def tokenize():
    return [
        """
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        """,
        """
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        """,
        """
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk import pos_tag

        def clear(file):

            sentences = sent_tokenize(file)
            words = word_tokenize(file)    
            words = [word.lower() for word in words if word.isalpha()]
            tags = pos_tag(words)

            print(f"Length of sentence: {len(sentences)}")
            for i, sentence in enumerate(sentences, start=1): 
                print(f"{i}: {sentence}")

            print(f"\nToatal number of words: {len(words)} \nWords: {words}\n")

            unique = set(words)
            print(f"Total Distinct words: {len(unique)}\n {unique}\n")

        clear(file)
        """
        
    ]