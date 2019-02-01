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

import metric
import sys

def score(model):
	for test_doc in model:
		for test_set in test_doc:
			_score(test_set)

def _score(test_set):
	idf_map = test_set['idf_map']
	doc = test_set['doc']
	for sentence in doc:
		sentence['tf-idf'] = map_to_tf_idf(sentence['vectors'],idf_map)
	
	questions = test_set['q']
	# score each questions
	for question in questions:
		problem = question['q_str']
		candidates = question['answer']

		# tf-idf!
		problem['tf-idf'] = map_to_tf_idf(problem['vectors'],idf_map)
		for candidate in candidates:
			candidate['tf-idf'] = map_to_tf_idf(candidate['value']['vectors'],idf_map)

		# scoring
		score_candidate(doc, problem, candidates)

def weighted_scoring(data, weight):
	for test_doc in data:
		for test_set in test_doc:
			_weighted_scoring(test_set,weight)
	return data

def _weighted_scoring(test_set,weight):
	for question in test_set['q']:
		for candidate in question['answer']:
			candidate['weighted_score'] = {feature: (score * weight[feature] if feature in weight else 0) for (feature, score) in candidate['score'].items()}

def score_candidate(doc, problem, candidates):
	scorer = metric.FeaturesScoring(doc,problem['tf-idf'])
	
	for candidate in candidates:
		score = {}
		score['cosine_matching'] = scorer.cosine_matching(problem['tf-idf'],candidate['tf-idf'],doc)
		score['closest_sentence'] = scorer.closest_sentence(problem['tf-idf'],candidate['tf-idf'],doc)
		score['greatest_matching'] = scorer.greatest_matching(problem['tf-idf'],candidate['tf-idf'],doc)
		score['closest_matching'] = scorer.closest_matching(problem['tf-idf'],candidate['tf-idf'],doc)
		score['greatest_cosine'] = scorer.greatest_cosine(problem['tf-idf'],candidate['tf-idf'],doc)
		score['average_cosine'] = scorer.average_cosine(problem['tf-idf'],candidate['tf-idf'],doc)
		det_unmatch(score)
		
		candidate['score'] = score

def det_unmatch(score):
	for feature, value in score.items():
		if value is None:
			score[feature] = 0.0
			score['unmatch'] = 1.0
		elif not ('unmatch' in score):
			score['unmatch'] = 0.0

def map_to_tf_idf(vectors, idf_map):
	tf_idf_map = {}
	for term, occ in vectors.items():
		tf_idf_map[term] = occ * (idf_map[term] if term in idf_map else idf_map['__default__'])
	return tf_idf_map


			
