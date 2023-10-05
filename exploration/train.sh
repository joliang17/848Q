#!/bin/bash

#SBATCH --job-name=bert_proj
#SBATCH --output=bert_proj.out.%j
#SBATCH --error=bert_proj.out.%j
#SBATCH --time=48:00:00
#SBATCH --account=scavenger 
#SBATCH --partition=scavenger
#SBATCH --gres=gpu:rtxa5000:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G

source /fs/nexus-scratch/yliang17/miniconda3/bin/activate expr

# guesser_size=40000
guesser_size=50000
buzzer_size=500

# #####################
# # GprGuesser (already trained by default)
# train guesser
# python3 guesser.py --guesser_type=GprGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=GprGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=500 

#####################
# TfidfGuesser v1
# # train guesser
# python3 guesser.py --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guesstrain.json.gz --logging_file=guesser.log --limit=${guesser_size}

# # eval guesser
# python3 eval.py --evaluate=guesser --guesser_type=TfidfGuesser --question_source=gzjson --questions=../data/qanta.guessdev.json.gz --limit=500 

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
#     --buzzer_type=BertBuzzer \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzztrain.json.gz \
#     --limit=5000 \
#     --features Length \
#     --buzzer_guessers TfidfGuesser \
#     --BertGuesser_filename=models/BertGuesser_tf > buzzer_train_tf.out

# # eval buzzer
# python3 eval.py \
#     --buzzer_type=BertBuzzer \
#     --evaluate=buzzer \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzzdev.json.gz \
#     --limit=500 \
#     --features Length \
#     --buzzer_guessers TfidfGuesser \
#     --BertGuesser_filename=models/BertGuesser_tf > buzzer_eval_tf.out


# gpt cache guesser
# python3 buzzer.py \
#     --buzzer_type=BertBuzzer \
#     --question_source=gzjson \
#     --questions=../data/qanta.buzztrain.json.gz \
#     --limit=500 \
#     --features Length \
#     --buzzer_guessers TfidfGuesser GprGuesser \
#     --BertGuesser_filename=models/BertGuesser_tf_v1 > buzzer_train_tf_v1.out

# eval buzzer
python3 eval.py \
    --buzzer_type=BertBuzzer \
    --evaluate=buzzer \
    --question_source=gzjson \
    --questions=../data/qanta.buzzdev.json.gz \
    --limit=500 \
    --features Length \
    --buzzer_guessers TfidfGuesser GprGuesser \
    --BertGuesser_filename=models/BertGuesser_tf_v1 > buzzer_eval_tf_v1.out