#!/usr/bin/python

# (C) Copyright 2013 Philip Arthur, NAIST
# 
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Lesser General Public License
# (LGPL) version 2.1 which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/lgpl-2.1.html
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

import sys
import util
from math import log	
from collections import Counter	
from metric import idf

# static initialization
n_gram = 3
def set_ngram(value):
	n_gram = value

def build_model(data):
	for test_document in data:
		for test_set in test_document:
			_build_model(test_set)
	return data

def _build_model(test_set):
	util.traverse_test_set_with_assignment(lambda x: build_n_gram(x,n_gram),test_set,list_method=True)
	util.traverse_test_set_with_assignment(transform_to_vector,test_set,list_method=True)
	idf_map = build_idf_map(test_set['doc'])
	test_set['idf_map'] = idf_map	

# Build_n_gram
# [(w1,t1),(w2,t2),(w3,t3),...,(wn,tn)] ->
# [(w1,t1),(w2,t2),(w3,t3),...,(wn,tn)] + [(w1_w2,'2-GRAM'),(w2_w3,2-GRAM'),(w3_w4,2-GRAM'),...,(wn-1_wn,2-GRAM')] + [3-gram] + ...
#           --- unigram ---                                         ---- bigram ---                              --- trigram ---
def build_n_gram(sentence,n_gram):
	temp_list = []
	try:
		for _n_gram in range(2,n_gram+1):
			for i in range(0,len(sentence)-_n_gram+1):
				word = '_'.join([tagged_word[0] for tagged_word in sentence[i:i+_n_gram]])
				temp_list.append(tuple((word, str(_n_gram) + '-GRAM')))
	except Exception:
		print sentence
		sys.exit(1)
	return sentence + temp_list

# Transform to Vector
# [(w1,t1),(w2,t2),(w3,t3),(w4,t4),...,(wn,tn)] ----->
# {
#   vectors: {
#		w'1 = len([w1 for w1 in previous list])
#   	w'2 = len([w2 for w2 in previous_list])
#   	....
#   	....
#   }
#   sentence = [(w1,t1),(w2,t2),(w3,t3),...,(wn,tn)]
# }
def transform_to_vector(_list):
	vectors = dict(Counter([tagged_word[0] for tagged_word in _list]))

	for k, v in vectors.items():
		if v == 0:
			print vectors
			sys.exit(1)

	return {'vectors': vectors, 'sentence': _list}

# Build IDF Map
# [
#	{
#   	vectors: {
#			w'1 = len([w1 for w1 in previous list])
#   		w'2 = len([w2 for w2 in previous_list])
#   		....
#   		....
#   	}
#   	sentence = [(w1,t1),(w2,t2),(w3,t3),...,(wn,tn)]
# 	},
#   ...
# ] ----->
# idf:{
# 	  w1 = idf(number of occurence w1 in document)
#     w2 = idf(number of occurence w2 in document)
#     .....
# }
def build_idf_map(sentences):
	sequence_of_words = {'__default__' : 0}
	for sentence in sentences:
		for word in sentence['vectors'].keys():
			if word in sequence_of_words:
				sequence_of_words[word] += 1
			else:
				sequence_of_words[word] = 1

	sequence_of_words = {k: idf(D=len(sentences),v=v) for k, v in sequence_of_words.iteritems()}
	
	if len(sentences) == 0:
		print >> sys.stdedd, "WARNING >> Only 1 sentence in document is detected."

	return sequence_of_words
