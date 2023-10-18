#!/bin/bash

#SBATCH --job-name=ft_sd_attn_debug_lyj
#SBATCH --output=ft_sd_attn_debug_lyj.out.%j
#SBATCH --error=ft_sd_attn_debug_lyj.out.%j
#SBATCH --time=36:00:00
#SBATCH --account=scavenger 
#SBATCH --partition=scavenger
#SBATCH --gres=gpu:rtxa5000:2
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G

# checking gpu status
nvidia-smi

# cd ../..
source /fs/nexus-scratch/yliang17/miniconda3/bin/activate expr

# guesser_size=40000
guesser_size=50000
buzzer_size=5000

#####################
# qanta test

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=TfidfGuesser --question_source=json --questions=../data/qanta.test.json --limit=-1 > guesser_eval.txt

# eval buzzer
# python3 eval.py \
#     --buzzer_type=LogisticBuzzer \
#     --evaluate=buzzer \
#     --question_source=json \
#     --questions=../data/qanta.test.json \
#     --limit=20 \
#     --features Length WikiScore Frequency GuessinQuestion  \
#     --buzzer_guessers TfidfGuesser \
#     --GprGuesser_filename=../models/gpt_cache.tar.gz > buzzer_eval.out


#####################
# Basic Version
# TfidfGuesser v1
# train guesser
# python3 guesser.py --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=-1   > guesser_eval.txt

# # gpt cache guesser
# python3 buzzer.py \
#     --buzzer_type=LogisticBuzzer \
#     --limit=${buzzer_size}  \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzztrain.json.gz \
#     --run_length=100 \
#     --features Length WikiScore Frequency GuessinQuestion \
#     --buzzer_guessers TfidfGuesser 

# # eval buzzer
# python3 eval.py \
#     --buzzer_type=LogisticBuzzer \
#     --evaluate=buzzer \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzzdev.json.gz \
#     --limit=-1 \
#     --features Length WikiScore Frequency GuessinQuestion \
#     --buzzer_guessers TfidfGuesser > buzzer_eval.out


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

####################
# train buzzer

# gpt cache guesser
python3 buzzer.py \
    --buzzer_type=BertBuzzer \
    --limit=${buzzer_size}  \
    --question_source=gzjson \
    --questions=../data/qanta.buzztrain.json.gz \
    --features Length \
    --buzzer_guessers TfidfGuesser \
    --run_length=100

# eval buzzer
python3 eval.py \
    --buzzer_type=BertBuzzer \
    --evaluate=buzzer \
    --question_source=gzjson \
    --questions=../data/qanta.buzzdev.json.gz \
    --limit=500 \
    --features Length \
    --buzzer_guessers TfidfGuesser > buzzer_eval.out
    # --features Length WikiScore Frequency GuessinQuestion  \
