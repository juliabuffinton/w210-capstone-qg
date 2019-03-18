from collections import Counter
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
import string
from collections import defaultdict

stop_words = set(stopwords.words('english')) 
punc = set(string.punctuation)

# Files from GenerationQ
with open(‘src-train.txt', 'r') as i:
  input = i.read()
with open(‘tgt-train.txt', 'r') as o:
  output = o.read()

# Get top 45k most frequent tokens from src-train
# Preprocessing: remove digits, stopwords (according to nltk), punctuation, and lowercase
wordcount = defaultdict(int)
for line in input.split(‘\n’):
	line = ''.join([x for x in line if not x.isdigit()])
	line = ''.join([x for x in line if x not in punc])
	line = ‘’.join([x.lower() for x in line])
	for word in word_tokenize(line):
    		if word not in stop_words:
       			 if word not in wordcount:
            			wordcount[word] = 1
        			else:
           			 wordcount[word] += 1
# write to input_45k file
counter_obj = Counter(wordcount)
file = open('input_45k.txt',"w")
for word,count in counter_obj.most_common(n=45000):
	file.write(word+'\n')

# Get top 28k most frequent tokens from tgt-train
# Preprocessing: remove digits, stopwords (according to nltk), punctuation, and lowercase
wordcount_output = defaultdict(int)
for line in output.split(‘\n’):
	line = ''.join([x for x in line if not x.isdigit()])
	line = ''.join([x for x in line if x not in punc])
	line = ‘’.join([x.lower() for x in line])
	for w in word_tokenize(line):
    		if word not in stop_words:
       			 if w not in wordcount_output:
            			wordcount_output[w] = 1
        			else:
           			 wordcount_output[w] += 1

# write to output_28k file
counter_obj_output = Counter(wordcount_output)
file_ouput = open(‘output_28k’,”w”)
for word,count in counter_obj_output.most_common(n=28000):
	file_ouput.write(word+'\n')
