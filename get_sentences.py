import sentence_selection
import json
from pprint import pprint

paragraphs = open("/home/joanna_huang/GenerationQ/model/bucket-w210/AA/wiki_00", "r")

f = open("new-sent-test.txt", "w+")
for p in paragraphs:
	data = json.loads(p)
	context = data['text']
	cleaned_data = sentence_selection.clean_sentences(context)
	word_distr = sentence_selection.word_distribution(cleaned_data)
	sentence_weight = sentence_selection.sentence_weight(word_distr,cleaned_data)
	chosen_sent = sentence_selection.topically_important_sentence(sentence_weight, context)
	for key,val in chosen_sent.items():
		f.write(str(val)+'.\n')

