# Jordan Boyd-Graber
# 2023
#
# Run an evaluation on a QA system and print results
import random
import numpy as np
from tqdm import tqdm

from buzzer import rough_compare

from params import load_guesser, load_questions, load_buzzer, \
    add_buzzer_params, add_guesser_params, add_general_params,\
    add_question_params, setup_logging

kLABELS = {"best": "Guess was correct, Buzz was correct",
           "timid": "Guess was correct, Buzz was not",
           "hit": "Guesser ranked right page first",
           "close": "Guesser had correct answer in top n list",
           "miss": "Guesser did not have correct answer in top n list",
           "aggressive": "Guess was wrong, Buzz was wrong",
           "waiting": "Guess was wrong, Buzz was correct"}

def eval_retrieval(guesser, questions, n_guesses=25, cutoff=-1):
    """
    Evaluate the guesser's retrieval
    """
    from collections import Counter, defaultdict
    outcomes = Counter()
    examples = defaultdict(list)

    question_text = []
    for question in tqdm(questions):
        text = question["text"]
        if cutoff == 0:
            text = text[:int(random.random() * len(text))]
        elif cutoff > 0:
            text = text[:cutoff]
        question_text.append(text)

    all_guesses = guesser.batch_guess(question_text, n_guesses)
    assert len(all_guesses) == len(question_text)
    for question, guesses, text in zip(questions, all_guesses, question_text):
        if len(guesses) > n_guesses:
            logging.warn("Warning: guesser is not obeying n_guesses argument")
            guesses = guesses[:n_guesses]
            
        top_guess = guesses[0]["guess"]
        answer = question["page"]

        example = {"text": text, "guess": top_guess, "answer": answer, "id": question["qanta_id"], "guesses": [(x["guess"], x["confidence"]) for x in guesses]}

        if any(rough_compare(x["guess"], answer) for x in guesses):
            outcomes["close"] += 1
            if rough_compare(top_guess, answer):
                outcomes["hit"] += 1
                examples["hit"].append(example)
            else:
                examples["close"].append(example)
        else:
            outcomes["miss"] += 1
            examples["miss"].append(example)

    return outcomes, examples

def pretty_feature_print(features, first_features=["guess", "answer", "id"]):
    """
    Nicely print a buzzer example's features
    """
    
    import textwrap
    wrapper = textwrap.TextWrapper()

    lines = []

    for ii in first_features:
        lines.append("%20s: %s" % (ii, features[ii]))
    for ii in [x for x in features if x not in first_features]:
        if isinstance(features[ii], str):
            if len(features[ii]) > 70:
                long_line = "%20s: %s" % (ii, "\n                      ".join(wrapper.wrap(features[ii])))
                lines.append(long_line)
            else:
                lines.append("%20s: %s" % (ii, features[ii]))
        elif isinstance(features[ii], float):
            lines.append("%20s: %0.4f" % (ii, features[ii]))
        else:
            lines.append("%20s: %s" % (ii, str(features[ii])))
    lines.append("--------------------")
    return "\n".join(lines)


def eval_buzzer(buzzer, questions):
    """
    Compute buzzer outcomes on a dataset
    """
    
    from collections import Counter, defaultdict
    
    buzzer.load()
    buzzer.add_data(questions)
    buzzer.build_features()
    
    predict, predict_score, feature_matrix, feature_dict, correct, metadata = buzzer.predict(questions)

    # Keep track of how much of the question you needed to see before
    # answering correctly
    question_unseen = {}
    question_length = defaultdict(int)
    
    outcomes = Counter()
    list_prob = defaultdict(list)
    examples = defaultdict(list)
    for buzz, buzz_score, guess_correct, features, meta in zip(predict, predict_score, correct, feature_dict, metadata):
        qid = meta["id"]
        
        # Add back in metadata now that we have prevented cheating in feature creation        
        for ii in meta:
            features[ii] = meta[ii]
        features['buzz_prob'] = buzz_score[1]

        # Keep track of the longest run we saw for each question
        question_length[qid] = max(question_length[qid], len(meta["text"]))
        
        if guess_correct:
            if buzz:
                outcomes["best"] += 1
                examples["best"].append(features)
                list_prob["best"].append(buzz_score[1])

                if not qid in question_unseen:
                    question_unseen[qid] = len(meta["text"])
            else:
                outcomes["timid"] += 1
                examples["timid"].append(features)
                list_prob["timid"].append(buzz_score[1])
        else:
            if buzz:
                outcomes["aggressive"] += 1
                examples["aggressive"].append(features)
                list_prob["aggressive"].append(buzz_score[1])

                if not qid in question_unseen:
                    question_unseen[qid] = -len(meta["text"])
            else:
                outcomes["waiting"] += 1
                examples["waiting"].append(features)
                list_prob["waiting"].append(buzz_score[1])

    unseen_characters = 0.0
    for question in range(len(question_length)):
        if question not in question_unseen:
            continue
        length = question_length[question]
        unseen_characters += (length - question_unseen[question]) / length
    return outcomes, list_prob, examples, unseen_characters
                

if __name__ == "__main__":
    # Load model and evaluate it
    import argparse
    
    parser = argparse.ArgumentParser()
    add_general_params(parser)
    add_guesser_params(parser)
    add_question_params(parser)
    add_buzzer_params(parser)

    parser.add_argument('--evaluate', default="buzzer", type=str)
    parser.add_argument('--cutoff', default=-1, type=int)    
    
    flags = parser.parse_args()
    setup_logging(flags)

    import pickle
    questions = load_questions(flags)
    guesser = load_guesser(flags, load=True)    
    if flags.evaluate == "buzzer":
        buzzer = load_buzzer(flags, load=True)
        outcomes, list_prob, examples, unseen = eval_buzzer(buzzer, questions)

        with open('buzzer.pkl', 'wb') as f:
            pickle.dump(examples, f)   
    elif flags.evaluate == "guesser":
        if flags.cutoff >= 0:
            outcomes, examples = eval_retrieval(guesser, questions, flags.num_guesses, flags.cutoff)
        else:
            outcomes, examples = eval_retrieval(guesser, questions, flags.num_guesses)

        with open('guesser.pkl', 'wb') as f:
            pickle.dump(examples, f)
    else:
        assert False, "Gotta evaluate something"
        
    total = sum(outcomes[x] for x in outcomes if x != "hit")
    with open('temp.txt', 'w') as f:
        for ii in outcomes:
            print("%s %0.2f\n===================\n" % (ii, outcomes[ii] / total))
            f.write("%s %0.2f\n===================\n" % (ii, outcomes[ii] / total))
            if len(examples[ii]) > 30:
                population = list(random.sample(examples[ii], 30))
            else:
                population = examples[ii]
            for jj in population:
                print(pretty_feature_print(jj))
                f.write(pretty_feature_print(jj) + '\n')
            print("=================") 
        
    total = sum(outcomes[x] for x in outcomes if x != "hit")
    for ii in outcomes:
        print("%s %0.2f\n" % (ii, outcomes[ii] / total))
        
    if flags.evaluate == "buzzer":
        for ii in outcomes:
            print("%s %0.2f %0.4f\n" % (ii, outcomes[ii] / total, np.mean(list_prob[ii])))

        for weight, feature in zip(buzzer._classifier.coef_[0], buzzer._featurizer.feature_names_):
            print("%40s: %0.4f" % (feature.strip(), weight))
        
        print("Questions Right: %i (out of %i) Accuracy: %0.2f  Buzz ratio: %0.2f Buzz position: %f" %
              (outcomes["best"], total, (outcomes["best"] + outcomes["waiting"]) / total,
               outcomes["best"] - outcomes["aggressive"] * 0.5, unseen))
    elif flags.evaluate == "guesser":
        precision = outcomes["hit"]/total
        recall = outcomes["close"]/total
        F1_score = (2*precision * recall)/(precision + recall)
        print("Precision @1: %0.4f Recall: %0.4f, F1: %0.4f" % (precision, recall, F1_score))
