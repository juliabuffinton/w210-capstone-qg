#!/usr/bin/env python3

import json
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument('--input-question-dir', type=str, default='/tmp',
                    help=('Directory to read original Wikipedia file from.'), required=True)
parser.add_argument('--input-sentence-dir', type=str, default='/tmp',
                    help=('Directory to read original Wikipedia file from.'), required=True)
parser.add_argument('--out-dir', type=str, default='/tmp',
                    help=('Directory to write squad-formatted file to '
                          '(wiki_XX.json)'), required=True)

args = parser.parse_args()
questions = args.input_question_dir
labeled_sents = args.input_sentence_dir
wiki_squad = args.out_dir

#################################################
#
# Begin processing
# Three steps to this. 
#
#################################################

total_questions = 0

for foldername in os.listdir(labeled_sents):
    
    input_subfolder_q = questions + foldername 
    input_subfolder_s = labeled_sents + foldername 
    output_subfolder = wiki_squad + foldername
    
    print("Adding questions to squad-formatted Wikipedia files in {} folder...".format(foldername))
    
    num_questions = 0 
    # each file represents several (variable #) wikipedia articles
    for filename in os.listdir(input_subfolder_q):
        
        # input file is questions with scores
        input_file_q = input_subfolder_q + '/' + filename
        input_file_s = input_subfolder_s + '/' + filename
        output_file = output_subfolder + '/' + filename
        
        with open(output_file) as json_file:  
            data = json.load(json_file)
        wiki_dict = data['data']
        
        with open(input_file_q) as f:
            pred_questions = f.read().splitlines()    
            pred_questions = pred_questions[::2] # start with the 1st line, take every other line
            
        with open(input_file_s) as f2:
            for line_q,line_s in zip(pred_questions,f2):
                #print(line_q)
                #print(line_s + '\n')
                line_tuple = eval(line_s)
                item_id = line_tuple[0]

                doc = wiki_dict[item_id[0]] # pull the whole document
                context = doc["paragraphs"][item_id[1]]

                num_questions += 1
                total_questions += 1
                context['qas'].append({"question": line_q.rstrip(), "answers": [], "id": str(item_id)})
            
        with open(output_file, 'w') as outfile:  
            json.dump(data, outfile)
    
    print("Completed adding {} questions to squad-formatted Wikipedia files in {} folder.\n".format(num_questions, foldername))

print("Complete. Added {} total questions to squad-formatted files.".format(total_questions))