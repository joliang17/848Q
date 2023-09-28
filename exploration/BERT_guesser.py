import torch
from transformers import BertTokenizer, BertModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tfidf_guesser import *


class BertEnhancedTfidfGuesser(TfidfGuesser):
    def __init__(self, filename, bert_model_name="bert-base-uncased", min_df=10, max_df=0.4):
        super().__init__(filename, min_df, max_df)

        # Check if a GPU is available and set the device accordingly
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print(f"Class currently being trained on {self.device}")
        # Initialize BERT tokenizer and model
        self.bert_model = BertModel.from_pretrained(bert_model_name).to(self.device)
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_model_name).to(self.device)
    
    def _get_bert_embeddings(self, questions):
        bert_embeddings = []
        for question in questions:
            tokens = self.bert_tokenizer(question, padding=True, truncation=True, return_tensors="pt")
            with torch.no_grad():
                output = self.bert_model(**tokens)
            cls_embedding = output.last_hidden_state[:, 0, :]
            bert_embeddings.append(cls_embedding)
        return torch.stack(bert_embeddings)
    
    def train(self, training_data, answer_field='page', split_by_sentence=True,
              min_length=-1, max_length=-1, remove_missing_pages=True):
        super().train(training_data, answer_field, split_by_sentence, min_length,
                      max_length, remove_missing_pages)
        
        # Get BERT embeddings for questions
        bert_embeddings = self._get_bert_embeddings(self.questions)
        
        # Combine BERT and TF-IDF embeddings
        combined_embeddings = torch.cat([bert_embeddings, self.tfidf], dim=1)
        
        # Convert combined embeddings to numpy arrays
        self.tfidf = combined_embeddings.numpy()
    
    def __call__(self, question, max_n_guesses=4):
        # Get BERT embeddings for the input question
        bert_embedding = self._get_bert_embeddings([question])
        
        # Concatenate BERT embedding with TF-IDF embeddings
        combined_embedding = torch.cat([bert_embedding, self.tfidf], dim=1)
        
        # Compute cosine similarities
        similarities = cosine_similarity(combined_embedding, self.tfidf)
        
        # Get top guesses
        top_indices = similarities.argsort()[0][::-1][:max_n_guesses]
        guesses = [{"question": self.questions[i], "guess": self.answers[i], "confidence": similarities[0][i]}
                   for i in top_indices]
        
        return guesses

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

    for qq, gg in zip(questions, guesses):
        print("----------------------")
        print(qq, gg)
