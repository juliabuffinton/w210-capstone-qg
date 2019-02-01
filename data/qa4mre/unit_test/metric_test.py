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

# Include upper directory
import sys
import math
import unittest
sys.path.insert(0, '..')

# Other imports
from metric import *

v1 = {
	'philip' : 1,
	'arthur' : 2,
	'is':1,
	'a':3,
	'student':5
}
v2 = {
	'student':2,
	'philip':1,
	'a':2,
	'research':1
}

class FundamentalTest(unittest.TestCase):

	# Dot Product and len
	def testOne(self):
		self.failUnless(dot_product(v1,v2) == (1*1 + 5*2 + 3*2))
		self.failUnless(norm_2(v1) == math.sqrt(1*1 + 2*2 + 1*1 + 3*3 + 5*5))
		self.failUnless(norm_2(v2) == math.sqrt(2*2 + 1*1 + 2*2 + 1*1))

	# Cosine Similarity
	def testTwo(self):
		self.assertEquals(sim(v1,v2),float(dot_product(v1,v2)) / (norm_2(v1) * norm_2(v2)))

	# Merge
	def testThree(self):
		v1_v2 = {
			'philip' : 2,
			'arthur' : 2,
			'is':1,
			'a':5,
			'student':7,
			'research':1
		}
		self.assertEquals(merge(v1,v2), v1_v2)

# Data for testing [Changes may harm test]
D = [
	# sentence 0
	{'tf-idf':{i : 1 for i in [1,3,5,10,11,12,13,14,15,16,17,18]}},
	# sentence 1
	{'tf-idf':{i : 1 for i in [1,2,3,10]}},
	# sentence 2
	{'tf-idf':{i : 1 for i in [2,4,5]}},
	# sentence 3
	{'tf-idf':{i : 1 for i in [2,5,6]}},
	# sentence 4
	{'tf-idf':{i : 1 for i in [1,2,5]}},
	# sentence 5
	{'tf-idf':{i : 1 for i in [3,4,5]}}
]

q = { i: 1 for i in [1] }

feat = FeaturesScoring(D,q)
class FeatureTest(unittest.TestCase):

	# cosine matching
	def testOne(self):
		self.assertEquals(feat.find_match(D,q), [0,1,4])

		D2 = { i: 1 for i in [6,11] }

		self.assertEquals(feat.find_match(D,D2), [0,3])
		self.assertEquals(feat.cosine_matching(q,D2,D), 1)

		D2 = { i: 1 for i in [4] }
		self.assertEquals(feat.find_match(D,D2), [2,5])
		self.assertEquals(feat.cosine_matching(q,D2,D), 0)

		D2 = { i: 1 for i in [1,2] }
		self.assertEquals(feat.find_match(D,D2), [0,1,2,3,4])
		self.assertEquals(feat.cosine_matching(q,D2,D), 3)

		

if __name__ == '__main__':
	unittest.main()