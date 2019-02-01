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
import java.io.Reader;
import java.io.StringReader;
import java.util.*;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.ling.HasWord;

// HOW TO COMPILE:
// javac -classpath [STANFORD_PARSER_JAR_PATH] StanfordNERServer.java
//

// EXECUTE: [from upper directory]
// java -classpath "/usr/share/stanford-ner/stanford-ner.jar:lib" StanfordNERServer 

public class StanfordParserServer {

	public static void main (String[] args) throws Exception {

		BufferedReader lreader = new BufferedReader(new InputStreamReader(System.in));
		BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(System.out));

		String line;
		while ((line = lreader.readLine()) != null) {
			Reader reader = new StringReader(line);
			DocumentPreprocessor dp = new DocumentPreprocessor(reader);

			List<String> sentenceList = new LinkedList<String>();
			Iterator<List<HasWord>> it = dp.iterator();
			while (it.hasNext()) {
			   StringBuilder sentenceSb = new StringBuilder();
			   List<HasWord> sentence = it.next();
			   for (HasWord token : sentence) {
			      if(sentenceSb.length()>1) {
			         sentenceSb.append(" ");
			      }
			      sentenceSb.append(token);
			   }
			   writer.write(sentenceSb.toString());
			   writer.newLine();
			}
			writer.flush();
			
		}
	}


}