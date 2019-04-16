#!/usr/bin/env python3

"""A script to re-format dumped Wikipedia in the format that SQuAD uses, for future processing and display."""

import json
import itertools
import ast
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument('--input-dir', type=str, default='/tmp',
                    help=('Directory to read original Wikipedia file from.'), required=True)
parser.add_argument('--out-dir', type=str, default='/tmp',
                    help=('Directory to write squad-formatted file to '
                          '(wiki_XX.json)'), required=True)

args = parser.parse_args()
wiki_dump = args.input_dir
wiki_squad = args.out_dir

#################################################
#
# Begin processing
#
#################################################


# iterate through dump of wikipedia articles
total_articles = 0
total_skipped = 0

for foldername in os.listdir(wiki_dump):
    
    input_subfolder = wiki_dump + foldername
    output_subfolder = wiki_squad + foldername
    
    if not os.path.exists(output_subfolder):
        os.mkdir(output_subfolder)

    # these are not files, just folders
    print("Processing files in {} folder...".format(foldername))
    num_articles = 0
    num_skipped = 0
    
    # each file represents several (variable #) wikipedia articles
    for filename in os.listdir(input_subfolder):
        if not filename.startswith('.'):
            f = open(input_subfolder + '/' + filename)

            # each file of articles will become a separate .json of articles
            # this helps if we run into issues, we can just discard a whole file and move on

            # set up json format for squad-like listing of articles
            wikipedia_data_dict = {"data": [], "version" : 1.0}

            # save this to the 'wikipedia_squad' folder of correctly-formatted dicts of wikipedia articles
            output_file = output_subfolder + '/' + filename

            # each line represents a different wikipedia article
            # we will ignore the id and url for now, not needed

            for line in f:
                line_dict = ast.literal_eval(line)
                title = line_dict['title']

                # for some reason, empty articles are included. They should be disregarded
                try:
                    text = line_dict['text'].split("\n\n",1)[1] # title is duplicated within text as well
                except:
                    num_skipped += 1
                    print("Skipping article:",title)
                else:
                    # arbitrary length, should eliminate articles like "disambiguation" articles, etc. 
                    if len(text) > 1000: 
                        num_articles += 1
                        # Break text up into paragraphs
                        paras = text.split("\n\n")

                        context = [{'context': para.rstrip(), 'qas' : []} for para in paras]

                        wikipedia_data_dict['data'].append({'title' : title, 'paragraphs' : context})

            # in case we don't have any articles in the file to add
            if (wikipedia_data_dict['data']): 
                with open(output_file, 'w') as outfile:  
                    json.dump(wikipedia_data_dict, outfile)
            
    total_articles += num_articles
    total_skipped += num_skipped
    
    print("Completing files in {} folder... {} articles processed, {} skipped.\n".format(foldername,num_articles,num_skipped))

print("Reformatting complete. Total {} articles processed for question generation, {} skipped.".format(total_articles,total_skipped))