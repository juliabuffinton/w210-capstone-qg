#!/bin/sh
generationq_dir="/home/julia_buffinton/GenerationQ/model"
model="${generationq_dir}/trained/600rnn_step_16000.pt" # updated to model with lowest perplexity
data_files="./wikipedia_data"
start_time=$(date "+%s")
files=0

# This should contain folders of files with sentences, that we will generate Qs for 
unlabeled_sents="${data_files}/unlabeled_sentences/"
questions="${data_files}/questions/"
wiki_squad="${data_files}/wikipedia_squad/"
labeled_sents="${data_files}/labeled_sentences/"

for foldername in $(ls ${unlabeled_sents})
do
    input_subfolder="${unlabeled_sents}${foldername}"
    output_subfolder="${questions}${foldername}"
    mkdir -p ${output_subfolder}
    echo "Beginning question generation for files in ${foldername} folder..."
    
    # each file represents questions for several (variable #) Wikipedia articles
    for filename in $(ls ${input_subfolder})
    do
        # input file is unlabeled sentence
        input_file="${input_subfolder}/${filename}"
        # save list of questions
        output_file="${output_subfolder}/${filename}"
        
        python -W ignore ${generationq_dir}/test.py -model "${model}" -src ${input_file} -output "${output_file}" -replace_unk -beam_size 3 -gpu 0 -batch_size 30
        now_time=$(date "+%s")
        files=`expr $files + 1`
        if [ `expr $files % 20` -eq 0 ]
        then
            if [ $files == 20 ]
            then
                time_taken=`expr $now_time - $start_time`
                echo "Processed 20 files in ${time_taken} seconds, total: ${files} files"
            else
                time_taken=`expr $now_time - $chunk_time`
                echo "Processed 20 files in ${time_taken} seconds, total: ${files} files"
            chunk_begin=${now_time}
            fi
        fi
    done    
done
total_time=`expr $now_time - $start_time`
echo "\nCompleted ${files} files in ${total_time} seconds"

python add_questions.py --input-question-dir ${questions} --input-sentence-dir ${labeled_sents} --out-dir ${wiki_squad}
        