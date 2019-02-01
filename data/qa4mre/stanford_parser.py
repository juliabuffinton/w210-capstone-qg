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

from subprocess import Popen, PIPE
from configuration import STANFORD_PARSER_JAR_PATH as parser_path

import shlex
import os

stanford_command = 'java -classpath "%s:lib" StanfordParserServer' % (parser_path)

def sentence_split(doc):

	process = Popen(shlex.split(stanford_command),stdin=PIPE,stdout=PIPE,bufsize=1)
	_out,_err = process.communicate(doc)
	
	_ret = []
	for sentence in _out.split('\n'):
		if len(sentence) > 0:
			_ret.append(sentence)

	return _ret
