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

import math

# NOTE: All of the metrics are the implementations of the following paper:
#	    http://www.phontron.com/paper/arthur13clef.pdf

threshold = 0.05 # l
LOG_BASE = 10

###
# -- IDF 
#                                     |D|
# idf(t,D) =  log (---------------------------------------------)
#                  1 + (number of sentence where term t occurs)
# log is in base 10
def idf(D,v):
	return math.log(float(D) / (1 + v), LOG_BASE)

# cosine similarity
# q and dj is already in tf-idf form
def sim(q,dj):
	len_q = norm_2(q)
	len_dj = norm_2(dj)
	return float(dot_product(q,dj)) / (len_q * len_dj) if len_q != 0 and len_dj != 0 else 0

# v1 and v2 are dictionary of occurences
def dot_product(v1,v2):
	return sum ([value * v2[word] for (word,value) in v1.items() if word in v2])

def norm_2(v):
	return math.sqrt(sum([x**2 for x in v.values()]))

def merge(v1,v2):
	v1_v2 = {_v2:v2_ for (_v2,v2_) in v2.items()}
	for key,value in v1.items():
		if key in v1_v2:
			v1_v2[key] += value
		else:
			v1_v2[key] = value
	return v1_v2 

class FeaturesScoring:

	def __init__(self,D,q):
		self.D1 = set(self.find_match(D,q))
		self.r = self.find_r(D,q)

	def greatest_cosine(self,q,ak,D):
		p = merge(q,ak)
		return float(max([sim(p,dj['tf-idf']) for dj in D]))

	def greatest_matching(self,q,ak,D):
		p = set(q.keys() + ak.keys()) # p is set of distinct keywords between question and candidate
		return float(max([len([x for x in dj.keys() if x in p]) for dj in D]))
		
	def cosine_matching(self,q,ak,D):
		D2 = set(self.find_match(D,ak))
		return float(len ([d for d in self.D1 if d in D2]))

	def closest_sentence(self,q,ak,D):
		D2 = set(self.find_match(D,ak))
		if len(self.D1) == 0 or len (D2) == 0:
			return None
		else:
			return float(min([abs(x-y) for x in self.D1 for y in D2]))

	def closest_matching(self,q,ak,D):
		if len(self.r) == 0:
			return None
		else:
			D2 = self.find_match(D, ak)
			if len(D2) != 0:
				return float(min([abs(x-y) for x in self.r for y in D2]))
			else:
				return None

	# this feature is not in the paper
	def average_cosine(self,q,ak,D):
		p = merge(q,ak)
		return float(sum([sim(p,dj['tf-idf']) for dj in D])/len(D))

	def find_match(self,doc, d):
		match = []
		for i in range (0,len(doc)):
			sentence = doc[i]
			if sim(sentence['tf-idf'], d) > threshold:
				match.append(i)
		return match

	def find_r(self,doc,q):
		r = set([])
		sentence_similarity = [sim(d['tf-idf'],q) for d in doc if sim(d['tf-idf'],q) > threshold]
		max_similarity = max(sentence_similarity) if len(sentence_similarity) > 0 else 0
		i = 0 
		for similarity in sentence_similarity:
			if similarity == max_similarity:
				r.add(i)
			i+=1
		return r
