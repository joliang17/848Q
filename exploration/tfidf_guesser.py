from typing import List, Optional, Tuple
from collections import defaultdict
import pickle
import json
import argparse
import os

from typing import Union, Dict
import math
import logging
from tqdm import tqdm

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

MODEL_PATH = 'tfidf.pickle'
INDEX_PATH = 'index.pickle'
QN_PATH = 'questions.pickle'
ANS_PATH = 'answers.pickle'

import os

from nltk.tokenize import sent_tokenize
from guesser import print_guess, Guesser


class DummyVectorizer:
    """
    A dumb vectorizer that only creates a random matrix instead of something real.
    """
    def __init__(self, width=50):
        self.width = width
        self.vocabulary_ = {}
    
    def transform(self, questions):
        import numpy as np
        return np.random.rand(len(questions), self.width)

class TfidfGuesser(Guesser):
    """
    Class that, given a query, finds the most similar question to it.
    """
    def __init__(self, filename, min_df=1, max_df=1.0):
        """
        Initializes data structures that will be useful later.

        filename -- base of filename we store vectorizer and documents to
        min_df -- we use the sklearn vectorizer parameters, this for min doc freq
        max_df -- we use the sklearn vectorizer parameters, this for max doc freq
        """

        # You'll need add the vectorizer here and replace this fake vectorizer
        stop = list(stopwords.words('english'))
        self.tfidf_vectorizer = TfidfVectorizer(min_df=min_df, max_df=max_df, stop_words=stop, sublinear_tf=True, ngram_range=(1,2))
        self.tfidf = None 
        self.questions = None
        self.answers = None
        self.filename = filename

    def train(self, training_data, answer_field='page', split_by_sentence=True,
                  min_length=-1, max_length=-1, remove_missing_pages=True):
        """
        The base class (Guesser) populates the questions member, so
        all that's left for this function to do is to create new members
        that have a vectorizer (mapping documents to tf-idf vectors) and
        the matrix representation of the documents (tfidf) consistent
        with that vectorizer.
        """

        Guesser.train(self, training_data, answer_field, split_by_sentence, min_length,
                          max_length, remove_missing_pages)

        self.tfidf = self.tfidf_vectorizer.fit_transform(self.questions)
        logging.info("Creating tf-idf dataframe with %i" % len(self.questions))
        
    def save(self):
        """
        Save the parameters to disk
        """
        
        path = self.filename
        os.makedirs(path, exist_ok=True)
        with open("%s.vectorizer.pkl" % path, 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)
        
        with open("%s.tfidf.pkl" % path, 'wb') as f:
            pickle.dump(self.tfidf, f)

        with open("%s.questions.pkl" % path, 'wb') as f:
            pickle.dump(self.questions, f)

        with open("%s.answers.pkl" % path, 'wb') as f:
            pickle.dump(self.answers, f)

    def __call__(self, question, max_n_guesses=4):
        """
        Given the text of questions, generate guesses (a list of both both the page id and score) for each one.

        Keyword arguments:
        question -- Raw text of the question
        max_n_guesses -- How many top guesses to return
        """

        # Compute the cosine similarity
        if isinstance(question, list):
            question = question[0]

        question_tfidf = self.tfidf_vectorizer.transform([question])
        cosine_similarities = cosine_similarity(question_tfidf, self.tfidf)

        cos = cosine_similarities[0]
        indices = cos.argsort()[::-1]

        guesses = []
        for i in range(max_n_guesses):
            idx = indices[i]
            guess =  {"question": self.questions[idx], "guess": self.answers[idx],
                    "confidence": cos[idx]}
            guesses.append(guess)
        return guesses

    def batch_guess(self, questions, max_n_guesses, block_size=1024):
        """
        The batch_guess function allows you to find the search
        results for multiple questions at once.  This is more efficient
        than running the retriever for each question, finding the
        largest elements, and returning them individually.  

        To understand why, remember that the similarity operation for an
        individual query and the corpus is a dot product, but if we do
        this as a big matrix, we can fit all of the documents at once
        and then compute the matrix as a parallelizable matrix
        multiplication.

        The most complicated part is sorting the resulting similarities,
        which is a good use of the argpartition function from numpy.
        """

        # IMPORTANT NOTE FOR HOMEWORK: you do not need to complete
        # batch_guess.  If you're having trouble with this, just
        # delete the function, and the parent class will emulate the
        # functionality one row at a time.
        
        from math import floor
    
        all_guesses = []

        logging.info("Querying matrix of size %i with block size %i" %
                     (len(questions), block_size))

        # The next line of code is bogus, this needs to be fixed
        # to give you a real answer.
        top_hits = np.array([list(range(max_n_guesses-1, -1, -1))]*block_size)
        for start in tqdm(range(0, len(questions), block_size)):
            stop = start+block_size
            block = questions[start:stop]
            logging.info("Block %i to %i (%i elements)" % (start, stop, len(block)))
            
            blocks_tfidf = self.tfidf_vectorizer.transform(block)
            cos_sim = cosine_similarity(blocks_tfidf, self.tfidf)
            cos_sim_idx = np.argsort(cos_sim, axis=-1)[:, ::-1]
            top_hits = cos_sim_idx[:, :max_n_guesses]

            for question in range(len(block)):
                guesses = []
                for idx in list(top_hits[question]):
                    score = cos_sim[question, idx]
                    guesses.append({"guess": self.answers[idx], "confidence": score, "question": self.questions[idx]})
                all_guesses.append(guesses)

        assert len(all_guesses) == len(questions), "Guesses (%i) != questions (%i)" % (len(all_guesses), len(questions))
        return all_guesses
    
    def load(self):
        """
        Load the tf-idf guesser from a file
        """
        
        path = self.filename
        with open("%s.vectorizer.pkl" % path, 'rb') as f:
            self.tfidf_vectorizer = pickle.load(f)
        
        with open("%s.tfidf.pkl" % path, 'rb') as f:
            self.tfidf = pickle.load(f)
        
        with open("%s.questions.pkl" % path, 'rb') as f:
            self.questions = pickle.load(f)

        with open("%s.answers.pkl" % path, 'rb') as f:
            self.answers = pickle.load(f)


if __name__ == "__main__":
    # Load a tf-idf guesser and run it on some questions
    from params import *
    logging.basicConfig(level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    add_general_params(parser)
    add_guesser_params(parser)
    add_question_params(parser)

    flags = parser.parse_args()
    
    guesser = load_guesser(flags, load=True)

    questions = ["This capital of England",
                 "The author of Pride and Prejudice",
                 "The composer of the Magic Flute",
                 "The economic law that says 'good money drives out bad'",
                 "located outside Boston, the oldest University in the United States"]

    guesses = guesser.batch_guess(questions, 3, 2)
    for pp, gg in list(zip(questions, guesses)):
        print(pp, gg)
        print("----------------------")

    # for question in questions:
    #     guesses = guesser(questions, 3)
    #     print(question)

    #     for gg in guesses:
    #         print(gg)

    #     print("----------------------")