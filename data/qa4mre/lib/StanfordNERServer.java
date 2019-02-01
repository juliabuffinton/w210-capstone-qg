/*
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
*/

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.BufferedWriter;
import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.CRFClassifier;

// HOW TO COMPILE:
// javac -classpath [STANFORD_NER_JAR_PATH] StanfordNERServer.java
//

// EXECUTE: [from upper directory]
// java -classpath "/usr/share/stanford-ner/stanford-ner.jar:lib" StanfordNERServer 

public class StanfordNERServer {

	public static void main (String[] args) throws Exception {
		BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
		BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(System.out));

		AbstractSequenceClassifier classifier = CRFClassifier.getClassifier(args[0]);

		String line;
		while ((line = reader.readLine()) != null) {
			String result = classifier.classifyToString(line);
			writer.write(result);
			writer.newLine();
			writer.flush();
			
		}
	}


}