# Author: Jordan Boyd-Graber
# 2013

# File to take guesses and decide if they're correct

import argparse
import string
import logging
import pickle
import pandas as pd

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
# from transformers import pipeline

from unidecode import unidecode
from tqdm import tqdm

from collections import Counter
from collections import defaultdict

from guesser import add_guesser_params
from features import LengthFeature
from params import add_buzzer_params, add_question_params, load_guesser, load_buzzer, load_questions, add_general_params, setup_logging

def normalize_answer(answer):
    """
    Remove superflous components to create a normalized form of an answer that
    can be more easily compared.
    """
    if answer is None:
        return ''
    reduced = unidecode(answer)
    reduced = reduced.replace("_", " ")
    if "(" in reduced:
        reduced = reduced.split("(")[0]
    reduced = "".join(x for x in reduced.lower() if x not in string.punctuation)
    reduced = reduced.strip()

    for bad_start in ["the ", "a ", "an "]:
        if reduced.startswith(bad_start):
            reduced = reduced[len(bad_start):]
    return reduced.strip()

def rough_compare(guess, page):
    """
    See if a guess is correct.  Not perfect, but better than direct string
    comparison.  Allows for slight variation.
    """
    # TODO: Also add the original answer line
    if page is None:
        return False
    
    guess = normalize_answer(guess)
    page = normalize_answer(page)

    if guess == '':
        return False
    
    if guess == page:
        return True
    elif page.find(guess) >= 0 and (len(page) - len(guess)) / len(page) > 0.5:
        return True
    else:
        return False
    
def runs(text, run_length):
    """
    Given a quiz bowl questions, generate runs---subsegments that simulate
    reading the question out loud.

    These are then fed into the rest of the system.

    """
    words = text.split()
    assert len(words) > 0
    current_word = 0
    last_run = 0

    for idx in range(run_length, len(text), run_length):
        current_run = text.find(" ", idx)
        if current_run > last_run and current_run < idx + run_length:
            yield text[:current_run]
            last_run = current_run

    yield text

def sentence_runs(sentences, run_length):
    """
    Generate runs, but do it per sentence (always stopping at sentence boundaries).
    """
    
    previous = ""
    for sentence in sentences:
        for run in runs(sentence, run_length):
            yield previous + run
        previous += sentence
        previous += "  "
    
class Buzzer:
    """
    Base class for any system that can decide if a guess is correct or not.
    """
    
    def __init__(self, filename, run_length, num_guesses=1):
        self.filename = filename
        self.num_guesses = num_guesses
        self.run_length=run_length
        
        self._runs = []
        self._questions = []
        self._answers = []
        self._training = []
        self._correct = []
        self._features = []
        self._metadata = []
        self._feature_generators = []
        self._guessers = {}

        logging.info("Buzzer using run length %i" % self.run_length)
        
        self._finalized = False
        self._primary_guesser = None
        self._classifier = None
        self._featurizer = None

    def add_guesser(self, guesser_name, guesser, primary_guesser=False):
        """
        Add a guesser identified by guesser_name to the set of guessers.

        If it is designated as the primary_guesser, then its guess will be
        chosen in the case of a tie.

        """

        assert not self._finalized, "Trying to add guesser after finalized"
        assert guesser_name != "consensus"
        assert guesser_name is not None
        assert guesser_name not in self._guessers
        self._guessers[guesser_name] = guesser
        if primary_guesser:
            self._primary_guesser = guesser_name

    def add_feature(self, feature_extractor):
        """
        Add a feature that the buzzer will use to decide to trust a guess.
        """

        assert not self._finalized, "Trying to add feature after finalized"
        assert feature_extractor.name not in [x.name for x in self._feature_generators]
        assert feature_extractor.name not in self._guessers
        self._feature_generators.append(feature_extractor)
        logging.info("Adding feature %s" % feature_extractor.name)
        
    def featurize(self, question, run_text, guess_history, guesses=None):
        """
        Turn a question's run into features.

        guesses -- A dictionary of all the guesses.  If None, will regenerate the guesses.
        """
        
        features = {}
        guess = None

        # If we didn't cache the guesses, compute them now
        if guesses is None:
            guesses = {}            
            for gg in self._guessers:
                guesses[gg] = self._guessers[gg](run_text)

        for gg in self._guessers:
            assert gg in guesses, "Missing guess result from %s" % gg
            result = list(guesses[gg])[0]
            if gg == self._primary_guesser:
                guess = result["guess"]

            # This feature could be useful, but makes the formatting messy
            # features["%s_guess" % gg] = result["guess"]
            features["%s_confidence" % gg] = result["confidence"]



        for ff in self._feature_generators:
            for feat, val in ff(question, run_text, guess):
                features["%s_%s" % (ff.name, feat)] = val

        return guess, features

    def finalize(self):
        """
        Set the guessers (will prevent future addition of features and guessers)
        """
        
        self._finalized = True
        if self._primary_guesser is None:
            self._primary_guesser = "consensus"
        
    def add_data(self, questions, answer_field="page"):
        """
        Add data and extract features from them.
        """
        
        self.finalize()
        
        num_questions = 0
        if 'questions' in questions:
            questions = questions['questions']
        for qq in tqdm(questions):
            answer = qq[answer_field]
            text = qq["text"]
            # Delete these fields so you can't inadvertently cheat while
            # creating features.  However, we need the answer for the labels.
            del qq[answer_field]
            if "answer" in qq:
                del qq["answer"]
            if "page" in qq:
                del qq["page"]
            del qq["first_sentence"]
            del qq["text"]
            
            for rr in runs(text, self.run_length):
                self._answers.append(answer)
                self._runs.append(rr)
                self._questions.append(qq)

    def build_features(self, history_length=0, history_depth=0):
        """
        After all of the data has been added, build features from the guesses and questions.
        """
        
        all_guesses = {}
        for guesser in self._guessers:
            all_guesses[guesser] = self._guessers[guesser].batch_guess(self._runs, self.num_guesses)
            logging.info("%10i guesses from %s" % (len(all_guesses[guesser]), guesser))
            assert len(all_guesses[guesser]) == len(self._runs), "Guesser %s wrong size" % guesser
            
        assert len(self._questions) == len(self._answers)
        assert len(self._questions) == len(self._runs)        
            
        num_runs = len(self._runs)

        logging.info("Generating all features")
        for question_index in tqdm(range(num_runs)):
            question_guesses = dict((x, all_guesses[x][question_index]) for x in self._guessers)
            guess_history = defaultdict(dict)
            for guesser in question_guesses:
                guess_history[guesser] = dict((time, guess[:history_depth]) for time, guess in enumerate(all_guesses[guesser]) if time < question_index and time > question_index - history_length)

            # print(guess_history)
            question = self._questions[question_index]
            run = self._runs[question_index]
            answer = self._answers[question_index]
            guess, features = self.featurize(question, run, question_guesses)
            
            self._features.append(features)
            self._metadata.append({"guess": guess, "answer": answer, "id": question["qanta_id"], "text": run})

            correct = rough_compare(guess, answer)
            logging.debug(str((correct, guess, answer)))
                
            self._correct.append(correct)
            assert len(self._correct) == len(self._features)
            assert len(self._correct) == len(self._metadata)
        
        assert len(self._answers) == len(self._correct), \
            "Answers (%i) does not match correct (%i)" % (len(self._answers), len(self._features))
        assert len(self._answers) == len(self._features)        

        if "GprGuesser" in self._guessers:
            self._guessers["GprGuesser"].save()
            
        return self._features
    
    def single_predict(self, run):
        """
        Make a prediction from a single example ... this us useful when the code
        is run in real-time.

        """
        
        guess, features = self.featurize(None, run)
        print("Trying to featurize")
        print(features)

        X = self._featurizer.transform([features])

        return self._classifier.predict(X), guess, features
    
           
    def predict(self, questions, online=False):
        """
        Predict from a large set of questions whether you should buzz or not.
        """
        
        assert self._classifier, "Classifier not trained"
        assert self._featurizer, "Featurizer not defined"
        assert len(self._features) == len(self._questions), "Features not built.  Did you run build_features?"
        X = self._featurizer.transform(self._features)
        if isinstance(self._classifier, LogisticRegression):
            return self._classifier.predict(X), X, self._features, self._correct, self._metadata
        else:
            clf = pipeline("text-classification", model=self._classifier, tokenizer=self.bert_tokenizer, device=self.device)
            input_seq = [self._metadata[i]['guess'] + '[SEP]' + self._metadata[i]['text'] for i in range(len(self._metadata))]
            results = clf(input_seq)
            predict_result = [item['label'] == 'LABEL_1' for item in results]
            predict_score = [item['score'] for item in results]
        
            return predict_result, X, self._features, self._correct, self._metadata
    
    def load(self):
        """
        Load the buzzer state from disk
        """
        
        with open("%s.featurizer.pkl" % self.filename, 'rb') as infile:
            self._featurizer = pickle.load(infile)        
    
    def save(self):
        """
        Save the buzzer state to disck
        """
        
        for gg in self._guessers:
            self._guessers[gg].save()
        with open("%s.featurizer.pkl" % self.filename, 'wb') as outfile:
            pickle.dump(self._featurizer, outfile)  
    
    def train(self):
        """
        Learn classifier parameters from the data loaded into the buzzer.
        """

        assert len(self._features) == len(self._correct)        
        self._featurizer = DictVectorizer(sparse=True)
        X = self._featurizer.fit_transform(self._features)
        metadata = self._metadata
        labeldata = self._correct
        return X, metadata, labeldata

if __name__ == "__main__":
    # Train a simple model on QB data, save it to a file
    import argparse
    parser = argparse.ArgumentParser()
    add_general_params(parser)
    add_guesser_params(parser)
    add_buzzer_params(parser)
    add_question_params(parser)
    flags = parser.parse_args()
    setup_logging(flags)    

    guesser = load_guesser(flags)    
    buzzer = load_buzzer(flags)
    questions = load_questions(flags)

    buzzer.add_data(questions)
    buzzer.build_features()

    buzzer.train()
    buzzer.save()

    if flags.limit == -1:
        print("Ran on %i questions" % len(questions))
    else:
        print("Ran on %i questions of %i" % (flags.limit, len(questions)))
    
