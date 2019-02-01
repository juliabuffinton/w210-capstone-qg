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
from tmert import c_at_1

def evaluate(test_model):
	total_correct, total_noa, total_question = 0,0,0
	for test_doc in test_model:
		for test_set in test_doc:
			correct, noa, n_question = _evaluate(test_set)
			total_correct += correct
			total_noa += noa
			total_question += n_question

	return c_at_1(float(total_correct), float(total_noa), float(total_question)) if total_question != 0 else 0

def _evaluate(test_set):
	correct, noa = 0, 0
	for question in test_set['q']:
		candidates = question['answer']
		system_answer = question['output']
		
		if system_answer is None:
			question['evaluation'] = 'NoA'
			noa += 1
		else:
			true_index = find_correct_answer(candidates)
			if true_index is None:
				print >> sys.stderr, "Error on question:" + " ".join(filter (lambda x: len(x.split("_")) == 1, question['q_str']))
				raise Exception('Could not find correct answer. Error on evaluation')

			if true_index == system_answer:
				question['evaluation'] = 'Correct'
				correct += 1
			else:
				question['evaluation'] = 'Incorrect'
	return correct, noa, len(test_set['q'])


def find_correct_answer(candidates):
	i = 0;
	for i in range (0, len(candidates)):
		candidate = candidates[i]
		if 'correct' in candidate:
			return i
	return None