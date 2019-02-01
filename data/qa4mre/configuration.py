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

# STANFORD NER
STANFORD_NER_PATH = '/usr/share/stanford-ner/'
STANFORD_NER_TAGSET_PATH = STANFORD_NER_PATH + 'classifiers/english.conll.4class.distsim.crf.ser.gz'
STANFORD_NER_JAR_PATH = STANFORD_NER_PATH + 'stanford-ner.jar'

# STANFORD PARSER
STANFORD_PARSER_PATH = '/usr/share/stanford-parser/'
STANFORD_PARSER_JAR_PATH = STANFORD_PARSER_PATH + 'stanford-parser.jar'

# Data
input = {
	'CLEF_2011_GS':'http://celct.fbk.eu/QA4MRE/scripts/downloadFile.php?file=/websites/ResPubliQA/resources/past_campaigns/2011/Training_Data/Goldstandard/QA4MRE-2011-EN_GS.xml',
	'CLEF_2012_GS': 'http://celct.fbk.eu/QA4MRE/scripts/downloadFile.php?file=/websites/ResPubliQA/resources/past_campaigns/2012/Main_Task/Training_Data/Goldstandard/Parallel_Aligned/QA4MRE-2012-EN_GS_SYNC.xml',
	'CLEF_2013_GS': 'http://celct.fbk.eu/QA4MRE/scripts/downloadFile.php?file=/websites/ResPubliQA/resources/past_campaigns/2013/Main_Task/Training_Data/Goldstandard/QA4MRE-2013-EN_GS.xml'
}