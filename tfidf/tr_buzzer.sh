#!/bin/bash

# guesser_size=40000
guesser_size=50000
buzzer_size=500

# # train guesser
# python3 guesser.py --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=500 

# train buzzer
python3 buzzer.py --guesser_type=TfidfGuesser --limit=${buzzer_size}  --question_source=gzjson --TfidfGuesser_filename=models/TfidfGuesser  --questions=../data/qanta.buzztrain.json.gz --run_length=400 --buzzer_guessers=TfidfGuesser

# eval buzzer
python3 eval.py --evaluate=buzzer --question_source=gzjson --questions=../data/qanta.buzzdev.json.gz --limit=500

