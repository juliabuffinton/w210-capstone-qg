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

import unittest

def build_name_txt(directory, url):
	return directory + "/" + url + ".txt"

def print_leaves(node,f=None):
	if isinstance(node,list) or isinstance(node,tuple):
		for item in node:
			print_leaves(item,f)
	elif isinstance(node,dict):
		for item in node.itervalues():
			print_leaves(item,f)
	else:
		if f != None:
			try:
				write_line(f,node)
			except Exception:
				print nod
		else:
			print node

def write_line(f,string=''):
	f.write(str(string)+'\n')

def traverse_test_set(action,test,list_method=False):
	for sentence in test['doc']:
		apply_action(action,sentence,list_method)
	for question in test['q']:
		apply_action(action,question['q_str'],list_method)
		for choice in question['answer']:
			apply_action(action,choice['value'],list_method)

def apply_action(action, item, list_method):
	if not list_method and isinstance(item,list):
		for i in range(0,len(item)):
			item[i] = action(item[i])
		return item
	else:
		return action(item)

def traverse_test_set_with_assignment(action,test,list_method = False):
	for i in range (0,len(test['doc'])):
		test['doc'][i] = apply_action(action,test['doc'][i],list_method)
	for question in test['q']:
		question['q_str'] = apply_action(action,question['q_str'],list_method)
		for choice in question['answer']:
			choice['value'] = apply_action(action,choice['value'],list_method)

def traverse_test_set_root(action,test_set,assignment=False,list_method = False):
	for test in test_set:
		if not assignment:
			traverse_test_set(action,test,list_method)
		else:
			traverse_test_set_with_assignment(action,test,list_method)

def traverse_all_test_sets(action,test_sets,assignment=False,list_method = False):
	for test_set in test_sets:
		traverse_test_set_root(action,test_set,assignment,list_method)

# Unit test
class TestCase(unittest.TestCase):
	def test_build_name_txt(self):
		self.assertEquals(build_name_txt('dir','file'),'dir/file.txt')

def _print(x):
	print x

if __name__ == "__main__":
	print print_leaves( {
      'answer': [
        {
          'value': 'the imprisonment of Nelson Mandela at Robben Island'
        },
        {
          'value': "the closing ceremony of Nelson Mandela's Foundation"
        },
        {
          'value': "the meeting with Youssou N'Dour"
        },
        {
          'value': 'the racial segregation in South Africa'
        },
        {
          'correct': True,
          'value': "Nelson Mandela's conference to the world press"
        }
      ],
      'q_str': 'What event caused Annie Lennox to commit herself to the fight against AIDS?'
    })
	unittest.main()

