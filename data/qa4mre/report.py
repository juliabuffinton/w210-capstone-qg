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

import os
import sys
from util import write_line as write

INDENT = 2
CHOICE = ['A','B','C','D','E','F','G']

def report(test_data, information,weight):
	output = [[] for i in range(0, sum([len(x) for x in test_data]))]
	# prepare to write
	with prepare_to_write() as f:
		# loop for each test-data
		index = 0
		for i in range(0,len(test_data)):
			write(f, 'Writing report for test data - ' + str(information[i]))
			for j in range(0, len(test_data[i])):
				deep_write(f,1,'Test Doc - [' + str(j+1) + ']')
				_report(f,test_data[i][j],weight,output[j])
				index += 1

		print_output(f,output)

	print >> sys.stderr, 'Finished writing a report to report/report.txt'

def _report(f,test_set,weight,output):
	doc = test_set['doc']

	deep_write(f,1,'Document')
	for sentence in doc:
		deep_write(f,2,viewable(sentence))
	deep_write(f,1,'Question')
	questions = test_set['q']
	for i in range(0,len(questions)):
		deep_write(f,2, str(i+1) + '. ' + viewable(questions[i]['q_str']))
		candidates = questions[i]['answer']
		deep_write(f,2, "System's Answer: " + (str(CHOICE[questions[i]['output']]) if questions[i]['output'] is not None else '-') + " ["+questions[i]['evaluation']+"]")

		if questions[i]['evaluation'] == 'Correct':
			output.append('_')
		elif questions[i]['evaluation'] == 'Incorrect':
			output.append(str(CHOICE[questions[i]['output']]))
		else: 
			output.append('?')

		for j in range(0,len(candidates)):
			deep_write(f,3, is_correct(CHOICE[j], candidates[j]) + '. ' + viewable(candidates[j]['value']))
			features = candidates[j]['score']
			weighted = candidates[j]['weighted_score']
			for feature, feat_value in features.items():
				deep_write(f,4,'- ' + feature + ' : ' + str(feat_value) + ' * ' + str(weight[feature]) + ' = ' + str(weighted[feature]))
			deep_write(f,4,"-" * 60 + '+')
			deep_write(f,4,"Total Score: " + str(candidates[j]['total_score']))
		write(f)

def print_output(f, output):
	max_len = max([len(x) for x in output])

	# header
	f.write('  ')
	for i in range(0,max_len):
		f.write(' ' + "%02d" %(i+1))
	f.write('\n')  

	# body
	for i in range(0,len(output)):
		f.write(("%02d" % (i+1)))
		for j in range (0, len(output[i])):
			f.write('  ' + output[i][j])
		f.write('\n')
	f.flush()

def is_correct(letter, candidate):
	if "correct" in candidate and candidate["correct"]:
		return "[" + letter + "]"
	else:
		return letter

def viewable(sentence):
	return ' '.join([word for (word, tag) in sentence['sentence'] if not '-' in tag])

def deep_write(f,deep,string):
	write(f,' ' * (INDENT*deep)  + str(string))

def prepare_to_write():
	if not os.path.exists("report"):
		os.makedirs("report")
	# note that report is intended for human reading not machine.
	return open("report/report.txt",'w') 
