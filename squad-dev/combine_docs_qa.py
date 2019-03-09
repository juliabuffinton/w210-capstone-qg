import json
import ast

with open('DrQA-input-squad-dev.json') as f:
  docs_qs = json.load(f)

ans_file = open('DrQA-input-squad-dev-single.preds','r')
answers = ast.literal_eval(ans_file.read())

docs_qa = {}
for key, value in docs_qs.items():
	qa = {}
	for k, v in answers.items():
		for q in range(len(value)):
			if int(k) == int(value[q][‘qid’]):
				qa[value[q][‘question’]] = v
	docs_qa[key] = qa

# with open('doc_qa-squad-dev.txt','w') as file:
#   file.write(json.dumps(docs_qa))

df = pd.DataFrame(columns =['text','qas'])
df['text'] = list(docs_qa.keys())
df['qas'] = list(docs_qa.values())
df.to_csv('docs_qa.csv')
