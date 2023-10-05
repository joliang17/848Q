#!/bin/bash

guesser_size=40000
# guesser_size=50000
buzzer_size=5000

# Basic Version
#####################
# TfidfGuesser v1
# train guesser
# python3 guesser.py --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# eval guesser
python3 eval.py --evaluate=guesser --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=-1   > guesser_eval.txt

# gpt cache guesser
# python3 buzzer.py \
#     --buzzer_type=LogisticBuzzer \
#     --limit=${buzzer_size}  \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzztrain.json.gz \
#     --run_length=100 \
#     --features Length \
#     --buzzer_guessers GprGuesser TfidfGuesser \
#     --GprGuesser_filename=../models/gpt_cache.tar.gz \

# eval buzzer
python3 eval.py \
    --buzzer_type=LogisticBuzzer \
    --evaluate=buzzer \
    --question_source=gzjson \
    --questions=../data/qanta.buzzdev.json.gz \
    --limit=-1 \
    --features Length \
    --buzzer_guessers GprGuesser TfidfGuesser \
    --GprGuesser_filename=../models/gpt_cache.tar.gz > buzzer_eval.out


# #####################

# #####################
# # GprGuesser (already trained by default)
# train guesser
# python3 guesser.py --guesser_type=GprGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=GprGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=500 

# ####################
# # TfidfGuesser v1
# # train guesser
# python3 guesser.py --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=500   > guesser_eval.txt

# # #####################
# # # TfidfGuesser v2

# # Run the first command
# python3 guesser.py \
#     --guesser_type=TfidfGuesser \
#     --question_source=gzjson \
#     --questions=../data/qanta.guesstrain.json.gz \
#     --logging_file=guesser.log \
#     --limit=200000  > guesser_train.txt

# # Run the second command
# python3 eval.py \
#     --evaluate=guesser \
#     --guesser_type=TfidfGuesser \
#     --question_source=gzjson \
#     --questions=../data/qanta.guessdev.json.gz \
#     --limit=300000  > guesser_eval.txt


#####################
# train buzzer

# # gpt cache guesser
# python3 buzzer.py \
#     --buzzer_type=LogisticBuzzer \
#     --limit=-1  \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzztrain.json.gz \
#     --run_length=100 \
#     --features Length \
#     --buzzer_guessers GprGuesser TfidfGuesser \
#     --GprGuesser_filename=../models/gpt_cache.tar.gz \

# # eval buzzer
# python3 eval.py \
#     --buzzer_type=LogisticBuzzer \
#     --evaluate=buzzer \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzzdev.json.gz \
#     --limit=-1 \
#     --features Length \
#     --buzzer_guessers GprGuesser TfidfGuesser \
#     --GprGuesser_filename=../models/gpt_cache.tar.gz > buzzer_eval.out

# # gpt cache guesser
# python3 buzzer.py \
#     --buzzer_type=LogisticBuzzer \
#     --limit=${buzzer_size}  \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzztrain.json.gz \
#     --run_length=100 \
#     --features Length WikiScore Frequency GuessinQuestion \
#     --buzzer_guessers GprGuesser TfidfGuesser \
#     --GprGuesser_filename=../models/gpt_cache.tar.gz \

# # eval buzzer
# python3 eval.py \
#     --buzzer_type=LogisticBuzzer \
#     --evaluate=buzzer \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzzdev.json.gz \
#     --limit=500 \
#     --features Length WikiScore Frequency GuessinQuestion  \
#     --buzzer_guessers GprGuesser TfidfGuesser \
#     --GprGuesser_filename=../models/gpt_cache.tar.gz > buzzer_eval.out
