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

import nltk
import util
import re
import sys
import simplejson as json
import qacache as cache
from stanford_ner import StanfordNER
from input_parser import parse
from util import traverse_all_test_sets as traverse_all
from stop_word_list import stop_word_list as stop_word_list
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
used_stop_word_list = stop_word_list - set([]) #exclusion list
def preprocess(testdoc,tag_ner=True):
	write_result(testdoc,'not-processed.txt')
	split_capital_word(testdoc)
	write_result(testdoc,'0-split-capital-word.txt')
	if tag_ner:
		StanfordNER(testdoc)

	write_result(testdoc,'1-named-entity-recognition.txt')
	
	# pos tagging
	print >> sys.stderr, "Begin POS-TAGGING",
	traverse_all(pos_tag, testdoc, assignment=True,list_method=True)
	write_result(testdoc, '1,5-pos-tagging.txt')
	print >> sys.stderr, "DONE"

	# lowercasing
	traverse_all(lambda x : [x[0].lower()] + x[1:],testdoc,assignment=True)

	# token-altering
	traverse_all(lambda x : [token_altering(x[0])] + x[1:],testdoc,assignment=True)

	# co-Reference Resolution
	write_result(testdoc, '2-token-altering-lowercasing.txt')
	coreference_resolution(testdoc)
	traverse_all(split_ne,testdoc, assignment=True,list_method=True)
	write_result(testdoc, '3-correference-resolution.txt')

	# only alpha numeric is allowed
	traverse_all(lambda x : [filter(lambda c: c.isalpha(), x[0])] + x[1:], testdoc,assignment=True)

	# stop word deletion
	traverse_all(lambda x: [""] + x[1:] if x[0] in used_stop_word_list else x,testdoc, assignment=True)

	# stemming
	traverse_all(lambda x : [lemmatize(x[0],x[1],x[2])] + x[1:],testdoc, assignment=True)

	# purging
	traverse_all(lambda x: filter(lambda y: len(y[0])!=0, x) ,testdoc, assignment=True,list_method=True)
	purge(testdoc)

	write_result(testdoc, '4-stop-word-cleaning-stemming.txt')
	return testdoc

######### POS TAG ###############################
tagger = nltk.data.load(nltk.tag._POS_TAGGER)
def pos_tag(sentence):
	_list = [w for (w,tag) in sentence]
	_tagged = tagger.tag(_list)
	
	for w,tag in zip(sentence,_tagged):
		w.append(tag[1])
	return sentence 

######### LEMMATIZATION
def lemmatize(word, ner_tag, pos_tag):
	tag = get_word_net_tag(pos_tag)
	return lemmatizer.lemmatize(word,tag) if ner_tag == 'O' and word != '' and tag != '' else word

# nltk.googlecode.com/svn/trunk/doc/api/nltk.corpus.reader.wordnet-module.html
def get_word_net_tag(pos_tag):
	if pos_tag[0] == 'J':
		return 'a'
	elif pos_tag[0] == 'N':
		return 'n'
	elif pos_tag[0] == 'V':
		return 'v'
	elif pos_tag[0] == 'R':
		return 'r'
	else:
		return ''

######### SPLIT CAPITAL WORD #####################
def split_capital_word(testsets):
	for test_doc in testsets:
		for test_set in test_doc:
			_split_capital_word(test_set)

def _split_capital_word(test_set):
	doc = []

	flag = False
	for sentence in test_set['doc']:
		s = ""
		for c in sentence:
			if flag and c.isupper():
				s += " "
				flag = False
			elif c == ' ':
				flag = False
			elif c.islower():
				flag = True
			s += c
		doc.append(s)
	test_set['doc'] = doc
	return test_set['doc']

######### CO-REFERENCE RESOLUTION ################
pronoun = set(['i','my','mine','she','he','it', 'his', 'her', 'they', 'them', 'their', 'him', 'himself', 'herself', 'myself', 'themselves', 'itself'])
tag_set = set(['PERSON', 'LOCATION', 'ORGANIZATION', 'MISC'])
look_up_threshold = 5
expected_map = {
	'i' : ['SPEAKER'],
	'my' : ['SPEAKER'],
	'mine' : ['SPEAKER'],
	'me' : ['SPEAKER'],
	'myself' : ['SPEAKER'],
	'she' : ['PERSON'],
	'he': ['PERSON'],
	'his': ['PERSON'],
	'him': ['PERSON'],
	'her': ['PERSON'],
	'himself': ['PERSON'],
	'herself': ['PERSON'],
	'it': set(['LOCATION', 'ORGANIZATION', 'MISC']),
	'itself': set(['LOCATION', 'ORGANIZATION', 'MISC']),
	'they': ['ORGANIZATION'],
	'them' : ['ORGANIZATION'],
	'their' : ['ORGANIZATION'],
	'themselves': ['ORGANIZATION']
	# TODO our and us!
}
def coreference_resolution(test_docs):
	for test_doc in test_docs:
		for test_set in test_doc:
			doc = test_set['doc']
			_coreference_resolution(doc)

def _coreference_resolution(test_doc):
	latest_ne = []	
	unreferenced_pronoun = {'SPEAKER': [], 'PERSON' : [], 'LOCATION': [], 'ORGANIZATION': [], 'MISC': [] }
	speaker = None
	for i in range(0,len(test_doc)): # test_doc[i] ==> sentence
		for j in range(0,len(test_doc[i])): # test_doc[i][j] ==> (WORD, NE_TAG)
			word, tag = test_doc[i][j][0], test_doc[i][j][1]
			if word in pronoun:
				expected_ne = expected_map[word]
				if 'SPEAKER' in expected_ne:
					if speaker != None:
						test_doc[i][j] = [speaker, 'PERSON'] + test_doc[i][j][2:]
					else:
						map (lambda x: unreferenced_pronoun[x].append((i,j)), expected_ne)
				else:
					ne_result = look_up_ne(expected_ne,latest_ne,look_up_threshold)
					if ne_result != None:
						test_doc[i][j] = ne_result
					else:
						map (lambda x: unreferenced_pronoun[x].append((i,j)), expected_ne)
			elif tag in tag_set:
				is_speaker = speaker == None and tag == 'PERSON'
				if is_speaker:
					speaker = word
				latest_ne = [[word,tag] + test_doc[i][j][2:]] + latest_ne
				if not unreferenced_pronoun[tag]: # there is some unreferenced NE
					reference_ne(latest_ne[0],unreferenced_pronoun['SPEAKER' if is_speaker else tag],test_doc)

	# for the remaining unreferenced, look up the entire latest_ne list
	for tag, unreferenced_list in unreferenced_pronoun.iteritems():
		for i,j in unreferenced_list:
			if test_doc[i][j][1] == 'O':
				ne = look_up_ne(tag,latest_ne,len(latest_ne))
				if ne != None:
					test_doc[i][j] = ne

def look_up_ne(expected, latest, look_up_threshold):
	for i in range (0, look_up_threshold):
		if i == len(latest):
			break
		elif latest[i][1] in expected: # latest[i] ==> (WORD,NE_TAG)
			return latest[i]
	return None

def reference_ne(ne,coordinate_list,target_doc):
	for i,j in coordinate_list:
		if target_doc[i][j][1] == 'O':
			target_doc[i][j] = ne

def split_ne(sentence):
	_list = []
	for word in sentence:
		_split = word[0].split('_')
		for _split_word in _split:
			_list.append([_split_word] + word[1:])
	return _list

######### PURGE ##################################
def purge(testdocs):
	for test_doc in testdocs:
		for test_set in test_doc:
			test_set['doc'] = filter (lambda x: len(x) != 0, test_set['doc'])

######### IO #####################################
def write_result(testdoc, name):
	f = cache.open_cache(name,'w')
	f.write(json.dumps(testdoc, sort_keys=True, indent=4 * ' '))
	f.close()

######### TOKEN ALTERING #########################
token_map = {
	"'m" : "am",
	"n't" : "not",
	"'s" : "is",
	"'re" : "are",
	"'d" : "would",
	"'ve" : "have",
	'll' : "will",
	"--lrb--":"(",
	"--rrb--":")"
}

def token_altering(token):
	return token_map[token] if token in token_map else token

if __name__ == "__main__":
	data = [parse("CLEF_2011_GS"), parse("CLEF_2012_GS")]
	preprocess(data)
