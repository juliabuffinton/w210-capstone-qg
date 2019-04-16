#!/bin/sh
qa_dir="/home/joanna_huang/DrQA"
model="${qa_dir}/data/reader/single.mdl"
qa_predict="${qa_dir}/scripts/reader/predict.py"
start_time=$(date "+%s")
files=0
data_files="./data/datasets"
# This should contain folders of files with lists of Wikipedia articles
wiki_squad="${data_files}/wikipedia_squad/"
answers="${data_files}/answers/"
ouput="${data_files}/for_autoq/"
for foldername in $(ls -1 ${wiki_squad})
do
    echo "foldername: ${foldername}"
    input_subfolder="${wiki_squad}${foldername}"
    output_subfolder="${answers}${foldername}"
    mkdir -p ${output_subfolder}
    echo "Beginning question answering for files in ${foldername} folder..."
    for filename in $(ls -1 ${input_subfolder})
    do
        echo "filename: ${filename}"
        input_file="${input_subfolder}/${filename}"
        output_file="${output_subfolder}/${filename}"
        python ${qa_predict} --model ${model} --out-dir ${output_subfolder} ${input_file}
        now_time=$(date "+%s")
        time_taken=`expr $now_time - $start_time`
        echo "Completed ${files} files in ${time_taken} seconds"
        files=`expr $files + 1`
    done
done

python add_answers.py --input-question-dir ${answers} --input-squad-dir ${wiki_squad} --out-dir ${wiki_squad}
