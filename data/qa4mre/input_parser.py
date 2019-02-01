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
import nltk
import re
import xml.etree.ElementTree as etree
from stanford_parser import sentence_split
from configuration import input as inp
from util import build_name_txt as build_name

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


def word_tokenize_and_filter(d):
	d = removeNonAscii(d)
	d = re.sub(r"\.{2,}",". ",d)
	d = re.sub(r"--", " ",d)
	d = re.sub(r"/", " ",d)
	d = re.sub(r" {2,}"," ",d)
	d = re.sub(r"\."," . ",d)
	return " ".join(nltk.word_tokenize(d))

def removeNonAscii(s): 
	return "".join(i for i in s if ord(i)<128)

def parse(filename):
	tree = etree.parse(build_name('input', filename))
	root = tree.getroot()

	tests = []
	for test in root.iter('reading-test'):
		doc = sentence_split(word_tokenize_and_filter(test.find('doc').text.encode('utf-8')))
		
		_questions = []
		for q_index in range (1,len(test)):
			question = test[q_index]
			q_str = word_tokenize_and_filter(question.find('q_str').text.encode('utf-8'))

			choices = []
			for c_index in range (1, len(question)):
				choice = question[c_index]
				_choice = {}
				_choice["value"] = word_tokenize_and_filter(choice.text.encode('utf-8'))
				if 'correct' in choice.attrib and choice.attrib['correct'].lower() == 'yes':
					_choice["correct"] = True
				choices.append(_choice)
			_questions.append({"q_str" : q_str, "answer" : choices})
		tests.append({'doc':doc, 'q': _questions})
	return tests

def get_example():
	return parse("CLEF_2011_GS")

if __name__ == "__main__":
	print(get_example()[0])

