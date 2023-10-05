# Jordan Boyd-Graber
# 2023
#
# Buzzer using BERT classification model

import os
import numpy as np
import pandas as pd
import torch
import pickle
from transformers import BertTokenizer, BertModel, BertForSequenceClassification, TrainingArguments, Trainer
from datasets import Dataset, load_metric, DatasetDict
metric = load_metric("accuracy")

from buzzer import Buzzer

class BertBuzzer(Buzzer):
    """
    BERT classifier to predict whether a buzz is correct or not.
    """
    def __init__(self, filename, run_length, num_guesses=1, bert_model_name='bert-base-uncased'):
        super().__init__(filename, run_length, num_guesses, )
        # Check if a GPU is available and set the device accordingly
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print(f"Class currently being trained on {self.device}")
        self.bert_model_name = bert_model_name
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_model_name)

    def process_data(self, metadata, o_label=None):
        def tokenize_function(examples):
            q_token = self.bert_tokenizer(examples["text"], padding="max_length", truncation=True)
            return q_token
        
        # For predicting use
        if o_label is None:
            label = [True] * len(metadata)
        else:
            label = o_label

        trans_datasets = []
        for data_idx, (meta, cur_l) in enumerate(zip(metadata, label)):
            # feature_x = X[data_idx]
            cur_l = 1 if cur_l else 0
            cur_data = {'labels': cur_l, 'text': meta["guess"] + '[SEP]' + meta["text"]}
            trans_datasets.append(cur_data)

        if o_label is not None:
            # split train & test data
            datasets = Dataset.from_pandas(pd.DataFrame(data=trans_datasets))
            train_testvalid = datasets.train_test_split(test_size=0.1)
            train_test_valid_dataset = DatasetDict({
                'train': train_testvalid['train'],
                'test': train_testvalid['test']})
            
            # tokenize sequence
            tokenized_datasets = train_test_valid_dataset.map(tokenize_function, batched=True)

            train_size = len(tokenized_datasets["train"])
            test_size = len(tokenized_datasets["test"])
            train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(min(train_size, 100))) 
            eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(min(test_size, 100))) 
            # train_dataset = tokenized_datasets["train"]
            # eval_dataset = tokenized_datasets["test"]

        else:
            # split train & test data
            datasets = Dataset.from_pandas(pd.DataFrame(data=trans_datasets))
            train_test_valid_dataset = DatasetDict({
                'eval': datasets,})
            eval_size = len(tokenized_datasets["eval"])
            train_dataset = tokenized_datasets["eval"]
            test_datasets = None
        
        return train_dataset, eval_dataset

    def train(self):

        def compute_metrics(eval_pred):
            logits, labels = eval_pred
            predictions = np.argmax(logits, axis=-1)
            return metric.compute(predictions=predictions, references=labels)
        
        X, metadata, label = Buzzer.train(self)
        
        train_dataset, eval_dataset = self.process_data(metadata, label)

        # Initialize BERT tokenizer and model
        training_args = TrainingArguments("BertBuzzer_trainer", evaluation_strategy="epoch")
        self._classifier = BertForSequenceClassification.from_pretrained(self.bert_model_name).to(self.device)
        trainer = Trainer(
                        model=self._classifier, 
                        args=training_args, 
                        train_dataset=train_dataset, 
                        eval_dataset=eval_dataset,
                        compute_metrics=compute_metrics,
                    )
        
        trainer.train()
        trainer.evaluate()
        trainer.save_model(self.filename)

    def save(self):
        Buzzer.save(self)

    def load(self):
        Buzzer.load(self)
        if os.path.exists(self.filename):
            self._classifier = BertForSequenceClassification.from_pretrained(self.filename).to(self.device)
        else:
            self._classifier = BertForSequenceClassification.from_pretrained(self.bert_model_name).to(self.device)
