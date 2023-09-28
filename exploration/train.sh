#!/bin/bash

# guesser_size=40000
guesser_size=50000
buzzer_size=500

# #####################
# # GprGuesser (already trained by default)
# train guesser
# python3 guesser.py --guesser_type=GprGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=GprGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=500 

# #####################
# # TfidfGuesser
# # train guesser
# python3 guesser.py --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=500 

#####################
# train buzzer

# # gpt cache guesser
# python3 buzzer.py \
#     --guesser_type=GprGuesser \
#     --limit=${buzzer_size}  \
#     --question_source=gzjson \
#     --GprGuesser_filename=../models/gpt_cache.tar.gz \
#     --questions=../data/qanta.buzztrain.json.gz \
#     --run_length=100 \
#     --buzzer_guessers GprGuesser TfidfGuesser

# eval buzzer
python3 eval.py \
    --evaluate=buzzer \
    --question_source=gzjson \
    --questions=../data/qanta.buzzdev.json.gz \
    --limit=500 \
    --GprGuesser_filename=../models/gpt_cache.tar.gz \
    --buzzer_guessers GprGuesser TfidfGuesser