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

from configuration import STANFORD_NER_TAGSET_PATH as tagset_path
from configuration import STANFORD_NER_JAR_PATH as jar_path
from util import traverse_test_set as traverse
from util import traverse_test_set_with_assignment as traverse_assignment
from util import traverse_test_set_root as traverse_root 
from subprocess import Popen, PIPE

import shlex
import os
import sys
import qacache
import util
import input_parser
import nltk

stanford_command = 'java -classpath "%s:lib" StanfordNERServer %s' % (jar_path,tagset_path)


class StanfordNER:
	def __init__(self, document_list):

		process = Popen(shlex.split(stanford_command),stdin=PIPE,stdout=PIPE,bufsize=1)

		_input = []
		for test_set_list in document_list:
			for test_set in test_set_list:
				for sentence in test_set['doc']:
					_input.append(sentence)

				for question in test_set['q']:
					_input.append(question['q_str'])
					for candidate in question['answer']:
						_input.append(candidate['value'])

		_input = '\n'.join(_input)
		_out,_err = process.communicate(_input)

		i=0
		result = _out.split('\n')
		for test_set_list in document_list:
			for test_set in test_set_list:
				tagged_sentence = []
				for sentence in test_set['doc']:
					tagged_sentence.append(self.read_ner(result[i]))
					i += 1

				test_set['doc'] = tagged_sentence

				for question in test_set['q']:
					question['q_str'] = self.read_ner(result[i])
					i+= 1

					tagged_sentence = []
					for candidate in question['answer']:
						candidate['value'] = self.read_ner(result[i])
						i+=1

	def read_ner(self,line):
		value = []
		tokens = line.strip().split(' ')
		_tag, _word, i = '','',0
		while i < len(tokens):
			word = tokens[i].split('/')
			if len(word) > 1:
				if word[1] != 'O':
					if _tag != '' and _tag != word[1]:
						value.append([_word, _tag])
						_word, _tag = '', ''
					if _word != '': _word += '_'
					_word += word[0]
					_tag = word[1]
				else:
					if _tag != '':
						value.append([_word,_tag])
						_word,_tag = '', ''
					value.append([word[0],word[1]])
				i += 1
		if len(_word) != 0:
			value.append([_word,_tag])
		return value

	def read_tagged(self,f,document_list):
		for document in document_list:
			traverse_root(lambda x: self.read_ner(f),document,assignment=True)

	def run_stanford_tagger(self):
		os.system(command)

	def write_test_set(self,f,test_set):
		traverse(lambda x: util.write_line(f,str(' '.join(nltk.word_tokenize(x)))),test_set)


if __name__ == '__main__':
	inp = input_parser.get_example()
	StanfordNER([[inp[0]]])
