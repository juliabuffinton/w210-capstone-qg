#!/usr/bin/env python3

import json
import itertools
import ast
import argparse
import os
import pandas as pd
from collections import defaultdict
import nltk
import string
import operator
import math
import re

#################################################
#
# Begin processing
# Three steps to this. 
#
#################################################

def sents_and_weights(d,paragraphs):
    """Clean sentences, remove digit, punctuation, upper case to lower
    Args: d,paragraphs = d is article number within file, paragraphs is just paragraphs
    Return: 
        labeled sentences: 
        stemmed sentences:
        word distribution: 
    """   
    # Create dictionaries for labeled & stemmed sentences to populate
    labeled_sentences = {}
    stemmed_sentences = {}

    # Create word distribution dictionaries
    # these needs to be a default dict so it returns 0 if word not found 
    word_cts = defaultdict(int)
    word_distr = defaultdict(int)

    # initialize for stemming
    stop_words = nltk.corpus.stopwords.words('english')
    stemmer = nltk.stem.PorterStemmer()
    tokenize = nltk.word_tokenize
    sent_splitter = nltk.data.load('tokenizers/punkt/english.pickle')

    # helper function for tracking stemmed words
    def stem_and_add(wd):
        word_cts[wd] += 1
        word_cts['total_count'] += 1
        return stemmer.stem(wd)

    # need to go through each 'paragraph' (context) to gather info about sentences
    for i,context in enumerate(paragraphs):

        paragraph = context['context']
        # split paragraph into sentences, make sure to keep digits, etc. together
        #sentences = context['context'].split('. ') #last one still has a period at the end

        #print(len(paragraph))

        if len(paragraph) > 75:
            sentences = sent_splitter.tokenize(context['context'].strip())
        else: 
            break

        # iterate through sentences to tokenize, calculate overall word distribution
        for j,original_sentence in enumerate(sentences):

            # Remove all digits
            sentence = ''.join([x for x in original_sentence if not x.isdigit()])
            # Remove all punctuation (OK to include periods since it's been split)
            sentence = ''.join([x for x in sentence if x not in string.punctuation])

            # Lowercase everything
            sentence = sentence.strip()
            sentence = sentence.lower()

            # Split into words & rejoin (remove extra spaces)
            sentence = ' '.join(sentence.split())

            tokenized_stemmed_sent = [stem_and_add(word) for word in nltk.tokenize.word_tokenize(sentence) 
                                      if not word in stop_words]

            # keep track of tokenized for calculating sentence weight in next step
            # save list of unprocessed sentences for later
            # but we're only selecting from the first and last sentences in the paragraphs
            if (original_sentence == sentences[0]) | (original_sentence == sentences[-1]):
                if not original_sentence.startswith('[[File:'):
                    labeled_sentences[(d,i,j)] = original_sentence.replace('\n', ' ')
                    stemmed_sentences[(d,i,j)] = tokenized_stemmed_sent

    # update our word dictionary to be relative frequencies rather than absolute values
    for word, ct in word_cts.items():
        # but keep our total count, we may want that later (not sure)
        if not word == 'total_count':
            word_distr[word] = word_cts[word] / word_cts['total_count']
            
    #print(sorted(word_distr.items(), key=lambda k: k[1], reverse=True))
    return labeled_sentences,stemmed_sentences,word_distr
    
def calc_sent_weight(word_dist, stemmed_sents):
        """Compute weight with respect to sentences
        Args:
                word_distribution: dict with word: weight
                stemmed_sents: list with 
        Return:
                sentence_weight: dict of weight of each sentence. key = sentence #, value = weight
        """
        sentences_weight = {}
        # Iterate through each word in each sentence, if word distribution and sentence id are in dictionary, 
        # add to existing word distribution. Else, sentence weight for given sentence equals current word distribution
          
        for key, words in stemmed_sents.items():
            #print(words)
            # Sentence weight equals sum of word distributions divided by length of cleaned sentence
            if len(words) == 0:
                weight = 0
            else:
                weight = sum([word_dist[word] for word in words]) / len(words)
            
            sentences_weight[key] = weight
            
        sentences_weight = sorted(sentences_weight.items(), key=operator.itemgetter(1), reverse=True)
        #print('sentence weight: ',sentences_weight)

        return sentences_weight
        
def topically_important_sentence(sentences_weight, labeled_sentences):
        """Select topically import sentences
        Args:
                sentence_weight: list of tuples, (sentence_num, sentence_weight) computed in sentence_weight
                paragraph: set of sentences
        Return:
                sentences_selected: dict, topically important sentences selected
        """
        final_sentences = {}
        
        total_sentences = len(sentences_weight)
        # how many sentences to retain
        num_sentences_selected = math.ceil(float(0.20) * total_sentences)
        
        # key of selected sentences (# order of sentence in paragraph)
        #sentences_selected_key = []
        
        # dictionary of all sentences 
        sentences_dict = {}
        flag = 0
        
        # select num_sentences_selected # of sentences from list of sentence weights
        selected_keys = [k for k,v in sentence_weight[0:num_sentences_selected]]

        for sent_key in selected_keys:
            pre_processed_sentence = labeled_sentences[sent_key]
            
            processed_sentence = pre_processed_sentence.lower() #lowercase
            processed_sentence = processed_sentence.replace('[[','') # remove brackets indicating links
            processed_sentence = processed_sentence.replace(']]','')
            processed_sentence = processed_sentence.replace(']','')
            processed_sentence = processed_sentence.replace('[','')
            processed_sentence = re.sub('(?<!\d)([.,!?()])(?<!\d)', r' \1 ', processed_sentence)
            processed_sentence = re.sub(r'\(','-lrb- ',processed_sentence) # replace left parens, add space after
            processed_sentence = re.sub(r'\)',' -rrb-',processed_sentence) # replace left parens, add space after
            processed_sentence = re.sub(r'\([^)]*\)', '',processed_sentence) #replace brackets in links
            processed_sentence = re.sub('(?<=\s)\"','`` ',processed_sentence) # replace first double quotes with ``
            processed_sentence = re.sub(r'\"', " ''", processed_sentence) # replace second double quote with two single quotes ''


            final_sentences[sent_key] = processed_sentence
            
        return final_sentences
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='setence_selection.py')
        
    parser.add_argument('--input-dir', type=str, default='./wikipedia_data/wikipedia_squad',
                    help=('Directory to read original squad-formatted file from.'), required=True)
    parser.add_argument('--out-dir-labeled', type=str, default='./wikipedia_data/labeled_sentences',
                    help=('Directory to read original squad-formatted file from.'), required=True)
    parser.add_argument('--out-dir-unlabeled', type=str, default='./wikipedia_data/unlabeled_sentences',
                    help=('Directory to read original squad-formatted file from.'), required=True)

    args = parser.parse_args()
    wiki_squad = args.input_dir
    labeled_sents = args.out_dir_labeled
    unlabeled_sents = args.out_dir_unlabeled
    total_skipped = 0
    total_selected = 0
    
    for foldername in os.listdir(wiki_squad):
    	input_subfolder = wiki_squad + foldername
    	output_subfolder_labeled = labeled_sents + foldername
    	output_subfolder_unlabeled = unlabeled_sents + foldername
    	
    	if not os.path.exists(output_subfolder_labeled):
    		os.mkdir(output_subfolder_labeled)
    		
    	if not os.path.exists(output_subfolder_unlabeled):
    		os.mkdir(output_subfolder_unlabeled)
    	
    	# these are not files, just folders
    	print("Selecting topical sentences for files in {} folder...".format(foldername))
    	
    	num_skipped = 0
    	num_selected = 0
    	
    	# each file represents several (variable #) wikipedia articles
    	for filename in os.listdir(input_subfolder):
    		input_file = input_subfolder + '/' + filename
    		
    		# save these to different directories of labeled and unlabeled sentences
    		output_file_labeled = open(output_subfolder_labeled + '/' + filename, "w")
    		output_file_unlabeled = open(output_subfolder_unlabeled + '/' + filename, "w")
    		
    		with open(input_file) as json_file:  
    			data = json.load(json_file)
    			
    		data = pd.DataFrame.from_dict(data)
    		df = data['data']
    		    		    		
 			# for each article in the file
    		for row,value in df.iteritems():
    		
    			try:
 					# here is where we clean and stem words, build word distribution
    				labeled_sentences, stemmed_sentences, word_distribution = sents_and_weights(row,value['paragraphs'])
    				
    				# use this word distribution to get weights for each sentence and calculate most important sentences 
    				sentence_weight = calc_sent_weight(word_distribution,stemmed_sentences)
    				
    				# pull out most important sentences
					# and keep track of where they came from: (doc #, context #, sentence #)
    				chosen_sentences = topically_important_sentence(sentence_weight,labeled_sentences)
    			except:
    				num_skipped += 1
    				print("Skipping article:",value['title'])
    			
    			else:
    				num_selected += 1
    				for sents in chosen_sentences.items():
    					#save selected sentences directly to file, for onmt model
    					output_file_unlabeled.write(str(sents[1])+'\n')
    					# keep track of their locations, though
    					output_file_labeled.write(str(sents)+'\n') 
    					
    	total_skipped += num_skipped
    	total_selected += num_selected
    	print("Completing files in {} folder... {} articles processed, {} articles skipped.\n".format(foldername,num_selected,num_skipped))
    	
    print("Sentence selection complete. Total {} articles processed, {} skipped for question generation.".format(total_selected, total_skipped))
