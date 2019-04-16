#!/usr/bin/env python3

import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input-answer-dir', type=str, default='/tmp',
                    help=('Directory to read answer file from.'), required=True)
parser.add_argument('--input-squad-dir', type=str, default='/tmp',
                    help=('Directory to read original Wikipedia file from.'), required=True)
parser.add_argument('--out-dir', type=str, default='/tmp',
                    help=('Directory to write squad-formatted file to '
                          '(wiki_XX.json)'), required=True)

args = parser.parse_args()
answers = args.input_answer_dir
wiki_squad = args.input_squad_dir
output = args.out_dir

#################################################
#
# Begin processing
# Three steps to this. 
#
#################################################


for foldername in os.listdir(answers):
    
    input_subfolder_a = answers + foldername 
    output_subfolder = output + foldername 
    squad_subfolder = wiki_squad + foldername
    
    if not os.path.exists(output_subfolder):
        os.mkdir(output_subfolder)
    
    print("Adding answers to squad-formatted Wikipedia files in {} folder...".format(foldername))
    
    # each file represents several (variable #) wikipedia articles
    for filename in os.listdir(input_subfolder_a):
        
        # input file is questions with scores
        input_file_a = input_subfolder_a + '/' + filename
        squad_file = squad_subfolder + '/' + filename[:7]
        output_file = output_subfolder + '/' + filename[:7]

        with open(squad_file) as json_file:  
            data = json.load(json_file)
        wiki_dict = data['data']

        with open(input_file_a) as f:
            qa_data = json.load(f)

            for key, value in qa_data.items():
                item_id = eval(key) 

                doc = wiki_dict[item_id[0]] # pull the whole document
                context = doc["paragraphs"][item_id[1]] # find the appropriate paragraph

                for i,question in enumerate(context['qas']):
                    #each paragraph may have several associated questions, so need to find the right one
                    if question['id'] == key:
                        #print(key)
                        question['answers'].append({'answer_start' : 0, 'text': value[0][0]})

        final_output = output_file + '.json'
        with open(final_output, 'w') as outfile:  
            json.dump(data, outfile)