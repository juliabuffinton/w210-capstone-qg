#!/usr/bin/env python3

import json
import ast
import numpy as np
import pandas as pd
import nltk
import spacy
import argparse
import os
from spacy import displacy
from collections import Counter
import random;random.seed(1)
import en_core_web_sm
import textacy
import re
import unidecode
from text2digits import text2digits
import time
t2d = text2digits.Text2Digits()
nlp = en_core_web_sm.load()


def preprocess(answer):
    # Remove extra punctuations and lowercase answer
    prep_answer = answer.lstrip('\'')
    prep_answer = prep_answer.rstrip('.')
    prep_answer = prep_answer.replace('\""','')
    prep_answer = prep_answer.replace('\"','')
    prep_answer = prep_answer.replace('\"','')
    prep_answer = prep_answer.lower()
    return prep_answer

def check_answer_type(raw_answer):
    answer_type = []
    tokenized_answer = nlp(preprocess(raw_answer))
    # get part of speech for answer
    pos_answer = [token.pos_ for token in tokenized_answer]
    # create month list to identify date answers
    month_list = ['january', 'jan', 'february', 'feb', 'march', 'april', \
                                   'may','june', 'july', 'august', 'aug', 'september', 'sept',\
                                   'october', 'oct', 'nov', 'dec','november', 'december']
    if raw_answer[0].isupper():
        # Check if it's a date
        if str(tokenized_answer[0]).lower() in month_list:
            answer_type.append('DATE')
        else:
            answer_type.append('PROPN')
    elif '°C' in raw_answer:
        answer_type.append('MEASUREMENT')
    elif (pos_answer[0]=='VERB') and (len(raw_answer)<2):
        answer_type.append('VERB')
    elif (pos_answer[0]=='VERB') and (len(raw_answer)>=2):
        answer_type.append('VP')
    # conditional for "to be" verbs
    elif (pos_answer[0]=='PART') and (pos_answer[1]=='VERB'):
        answer_type.append('VP')
    elif (pos_answer[0]=='ADV'):
        if len(tokenized_answer)>1:
            if (pos_answer[1]=='ADJ'):
                answer_type.append('ADJ')
            elif (pos_answer[1]=='PUNCT') and (pos_answer[2]=='ADJ'):
                answer_type.append('ADJ')
            elif (pos_answer[1]=='VERB'):
                answer_type.append('VP')
            else:
                answer_type.append('ADV')
        else:
            answer_type.append('ADV')
    elif (pos_answer[0]=='NUM') |  (pos_answer[0]=='PUNCT'):
        month_present = [1 for i in month_list if i in raw_answer.lower()]
        BC_AD = [1 for i in ['AD','BC'] if i in raw_answer.lower()]
        measurement_present = [1 for i in ['minutes', 'hours', 'seconds', 'days','%','°C','°F'] if i in raw_answer]
        if month_present!=[]:
            answer_type.append('DATE')
        elif BC_AD!=[]:
            answer_type.append('YEAR')
        elif measurement_present!=[]:
            answer_type.append('MEASUREMENT')
        else:
            answer_type.append('NUM')
    elif pos_answer[0]=='ADJ':
        answer_type.append('ADJ')
    elif (pos_answer[0]=='NOUN') | (pos_answer[0]=='X'):
        month_present = [1 for i in month_list if i in raw_answer.lower()]
        # check if it's a hyphen-separated adjective
        if re.findall(r'\w+(?:-\w+)+'.lower(),raw_answer):
            answer_type.append('ADJ')
        # check if there's a digit in the answer
        elif bool(re.search(r'\d', raw_answer)):
             # check for currency symbols
            if bool(re.search(r'([£\$€])', raw_answer)):
                answer_type.append('MONEY')
            elif str(tokenized_answer[1])=='-':
                answer_type.append('SCORE')
            elif month_present!=[]:
                answer_type.append('DATE')
            else:
                answer_type.append('YEAR')
        else:
            answer_type.append('NOUN')
    elif pos_answer[0]=='ADP':
        answer_type.append('ADP')
    elif pos_answer[0]=='DET':
        if pos_answer[1]=='NOUN':
            answer_type.append('NOUN')
        elif pos_answer[1]=='PROPN':
            answer_type.append('PROPN')
    elif pos_answer[0]=='SYM':
        answer_type.append('MONEY')
    else:
        answer_type.append('Unknown type')
    return answer_type

def generate_distractor(topic, paragraph, qid, question, answer, answer_type):
    wrong_answers=[]
    #preprocess answer
    correct_answer = nlp(unidecode.unidecode(preprocess(answer)))
    # get answer pos
    ans_length = len(correct_answer)
    ans_tag = [token.tag_ for token in correct_answer]
    ans_pos = [token.pos_ for token in correct_answer]
    # tokenize paragraph
    article = nlp(unidecode.unidecode(paragraph))
    doc = textacy.Doc(paragraph, lang='en_core_web_sm')
        
    # Preprocessing for same sentence distractor generation
    # get all sentences in paragraph
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sent_list = sent_detector.tokenize(paragraph.strip())

    # find sentence that has answer
    for s in sent_list:
        if answer in s:
            ans_sent = s
    # tokenize sentence
    sentence = nlp(ans_sent)
    sent = textacy.Doc(sentence, lang='en_core_web_sm')
        
    # Preprocessing for same topic distractor generation
    # choose random paragraph from same topic
    topic_index = next((index for (index, d) in enumerate(df['data']) if d["title"] == topic), None)
    index_list = list(range(len(df['data'][topic_index]['paragraphs'])))
    # make sure isn't the same paragraph as current paragraph
    p_index = next((index for (index, d) in enumerate(df['data'][topic_index]['paragraphs'])\
                    if d["context"] == paragraph), None)
    index_list.remove(p_index)
    # Choose 5 random paragraphs from the same article
    alt_p_index = random.choices(index_list,k=5)
    alt_p_list = [df['data'][topic_index]['paragraphs'][i]['context'] for i in alt_p_index]
    alt_article_list = [nlp(alt_p) for alt_p in alt_p_list]
    alt_paragraph_list = [textacy.Doc(alt_p, lang='en_core_web_sm') for alt_p in alt_p_list]
    
    ent_list = [str(i).lower() for i in list(article.ents)]
#     print('ent_list: ' + str(ent_list))
#     print('correct answer: ' + str(correct_answer))
    if str(correct_answer) in ent_list:
        answer_type.append('ENTITY')    
#         print('in entity list')
        ent_labels = [x.label_ for x in article.ents]
        # get all named entities in sentence
        sent_ent_list = [str(i).lower() for i in list(sentence.ents)]
        sent_labels = [x.label_ for x in sentence.ents]
        alt_article_ent_list = []
        alt_article_labels = []
        for p in alt_article_list:
            p_ent_list = [str(i).lower() for i in list(p.ents)]
            p_labels = [x.label_ for x in p.ents]
            alt_article_ent_list.extend(p_ent_list)
            alt_article_labels.extend(p_labels)
#         print('alt_article_ent: ' + str(alt_article_ent_list))
#         print('alt_article_labels: ' + str(alt_article_labels))
        merged=set(ent_labels+sent_ent_list+alt_article_ent_list)
        max_length = max(len(ent_list), len(sent_ent_list), len(alt_article_ent_list))
        # create table of named entities

        ne_pd = pd.DataFrame()
        ne_pd['entity'] = ent_list + (['NA'] * (max_length - len(ent_list)))
        ne_pd['label'] = list(ent_labels) + (['NA'] * (max_length - len(ent_list)))
        ne_pd['sent_entity'] = sent_ent_list + (['NA'] * (max_length - len(sent_ent_list)))
        ne_pd['sent_label'] = list(sent_labels) + (['NA'] * (max_length - len(sent_ent_list)))
        ne_pd['altp_entity'] = alt_article_ent_list + (['NA'] * (max_length - len(alt_article_ent_list)))
        ne_pd['altp_label'] = list(alt_article_labels) + (['NA'] * (max_length - len(alt_article_ent_list)))


        ans_label = [ne_pd[ne_pd['entity']==e]['label'].values[0] for e in ne_pd['entity'] if e in str(correct_answer)]
#         print('answer label: ' + str(ans_label))
        # This filters scores such as 49-15 that are labeled as "DATE"
        
                    
        alt_ans_list = list(ne_pd[(ne_pd['label'].isin(ans_label))]['entity'])
        alt_ans_list.extend(list(ne_pd[(ne_pd['sent_label'].isin(ans_label))]['sent_entity']))
        alt_ans_list.extend(list(ne_pd[(ne_pd['altp_label'].isin(ans_label))]['altp_entity']))
#         print('alt_ans_list: ' + str(alt_ans_list))
        if (['DATE'] in ans_label) | (ans_label==['DATE']):
            score_list=[]
            if 'SCORE' in answer_type:
                num_list = re.findall(r'(\d+-?){1,2}',paragraph)
                # Iterate through same topic articles to find all numbers
                for p in alt_p_list:
                    num_list.extend(re.findall(r'(\d+-?){1,2}',p))
                    for n in range(len(num_list)-1):
                        score = num_list[n][:2]+'-'+num_list[n+1][:2]
                        score_list.append(score)
                wrong_answers = score_list
            else:

                filtered_month = set(['January', 'Jan', 'February', 'March', 'April', \
                                           'May','June', 'July', 'August', 'September', \
                                           'October','November','December'])-set([(str(correct_answer[0]).capitalize())])
                month_list=random.sample(filtered_month,5)
                day_list = random.sample(range(1, 30), 5)
                year_list = random.sample(range(1300,2050), 5)
                random_date = [str(m)+' '+str(d)+','+str(y) for m in month_list for d in day_list for y in year_list]
                alt_ans_list.extend(random_date)
        if len(alt_ans_list)<=3:
            if (['TIME'] in ans_label) | (ans_label==['TIME']) | (['PERCENT'] in ans_label) | (ans_label==['PERCENT']):
                random_time = [str(num)+' ' +str(correct_answer[-1]) for num in random.sample(range(1, 60), 5)]
                alt_ans_list.extend(random_time)
            elif (['MONEY'] in ans_label) | (ans_label==['MONEY']):
                currency = answer[0]
                random_money = [answer[0]+str(num)+' ' +str(correct_answer[-1]) for num in random.sample(range(1, 60), 5)]
                alt_ans_list.extend(random_money)
            elif (['DATE'] in ans_label) | (ans_label==['DATE']):
                filtered_month = set(['January', 'Jan', 'February', 'March', 'April', \
                                           'May','June', 'July', 'August', 'September', \
                                           'October','November','December'])-set([(str(correct_answer[0]).capitalize())])
                month_list=random.sample(filtered_month,5)
                day_list = random.sample(range(1, 30), 5)
                year_list = random.sample(range(1300,2050), 5)
                random_date = [str(m)+' '+str(d)+','+str(y) for m in month_list for d in day_list for y in year_list]
                alt_ans_list.extend(random_date)
            elif (['ORDINAL'] in ans_label) | (ans_label==['ORDINAL']) | (['CARDINAL'] in ans_label) | (ans_label==['CARDINAL']):
#                 print('answer is ORDINAL')
                correct_ans_pos = str(['r'+str(token.pos_)+'l' for token in \
       correct_answer])[1:-1].replace("'r","<").replace("l'",">").replace(',','+',1).replace(',','*').replace(' ','')+'+'
#                 print(correct_ans_pos)
                alt_ans_list=[]
                for p in alt_paragraph_list:
                    p_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(p, correct_ans_pos)]
                    alt_p_list.extend(p_list)
                alt_ans_list.extend(alt_p_list)
            else:
                correct_ans_pos = str(['r'+'PROPN'+'l' for token in \
       correct_answer])[1:-1].replace("'r","<").replace("l'",">").replace(',','+',1).replace(',','*').replace(' ','')+'+'
                alt_ans_list=[]
                for p in alt_paragraph_list:
                    p_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(p, correct_ans_pos)]
                    alt_p_list.extend(p_list)
                alt_ans_list.extend(alt_p_list)
        wrong_answers = alt_ans_list

        
    elif 'PROPN' in answer_type:
        doc_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(doc, r'<PROPN>+')]
        sent_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(sent, r'<PROPN>+')]
        alt_p_list=[]
        for p in alt_paragraph_list:
            p_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(p, r'<PROPN>+')]
            alt_p_list.extend(p_list)
        merged = set(doc_list+sent_list+alt_p_list)
        wrong_answers=merged    
    elif 'NUM' in answer_type:
        
        doc_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(doc, r'<NUM>+')]
        sent_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(sent, r'<NUM>+')]
        alt_p_list=[]
        for p in alt_paragraph_list:
            p_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(p, r'<NUM>+')]
            alt_p_list.extend(p_list)
        merged = set(doc_list+sent_list+alt_p_list)
        wrong_answers = [t2d.convert(str(i)).lstrip() for i in merged]
        if len(str(correct_answer))==4:
            wrong_answers = [i if len(i)==4 else str(correct_answer)[:2]+str(random.sample(range(0, 99),1)[0]) for i in wrong_answers]
    
    elif 'DATE' in answer_type:
        filtered_month = set(['January', 'Jan', 'February', 'March', 'April', \
                                           'May','June', 'July', 'August', 'September', \
                                           'October','November','December'])-set([(str(correct_answer[0]).capitalize())])
        month_list=random.sample(filtered_month,5)
        if ans_length==1:
            wrong_answers=month_list
        else:
            day_list = random.sample(range(1, 30), 5)
            year_list = random.sample(range(1300,2050), 5)
            random_date = [str(m)+' '+str(d)+','+str(y) for m in month_list for d in day_list for y in year_list]
            wrong_answers=random_date
    else:
        merged=[]
        
        correct_ans_pos = str(['r'+str(token.pos_)+'l' for token in \
           correct_answer])[1:-1].replace("'r","<").replace("l'",">").replace(',','+',1).replace(',','*').replace(' ','')+'+'
#         print('correct_ans_pos: ' + str(correct_ans_pos))
        doc_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(doc, correct_ans_pos)]
        sent_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(sent, correct_ans_pos)]
        alt_p_list=[]
        for p in alt_paragraph_list:
            p_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(p, correct_ans_pos)]
            alt_p_list.extend(p_list)
        merged = set(doc_list+sent_list+alt_p_list)
        wrong_answers=list(merged)

        if len(wrong_answers)<=3:
            if '<NOUN>' in correct_ans_pos:
                for p in alt_paragraph_list:
                    p_list = [l.text.lower() for l in textacy.extract.pos_regex_matches(p,r'<NOUN>+')]
                    wrong_answers.extend(p_list)
                    
            elif '<VERB>' in correct_ans_pos:
                for p in alt_paragraph_list:
                    p_list = [l.text.lower()for l in textacy.extract.pos_regex_matches(p,r'<VERB>+')]
                    wrong_answers.extend(p_list)
                    
        if 'VP' in answer_type:
            if len(wrong_answers) >= 3:
                for i in wrong_answers:
                    if isinstance(i, str):
                        item = nlp(i)
                        if (item[0].tag_ == ans_tag[0]) and (item[-1].pos_ == ans_pos[-1]):
                            wrong_answers.append(item)
        
        if 'VERB' in answer_type:
            if len(wrong_answers) >= 3:
                for i in wrong_answers:
                    if isinstance(i, str):
                        item = nlp(i)
                        if (item[0].tag_ == ans_tag[0]):
                            wrong_answers.append(item.orth_)
        
        if 'ADJ' in answer_type:
            hyphen_sep_words = re.findall(r'\w+(?:-\w+)+'.lower(),paragraph)
            hyphen_sep_words_sent = re.findall(r'\w+(?:-\w+)+'.lower(),ans_sent)
            alt_p_hyphen_sep_words=[]
            for p in alt_p_list:
                p_hyphen_sep_words = re.findall(r'\w+(?:-\w+)+'.lower(),p)
                alt_p_hyphen_sep_words.extend(p_hyphen_sep_words)
#             alt_topic_hyphen_sep_words = re.findall(r'\w+(?:-\w+)+'.lower(),alt_topic_paragraph)

            hyphen_words = hyphen_sep_words+hyphen_sep_words_sent+alt_p_hyphen_sep_words
#             print('hyphen_words: ' + str(hyphen_words))
            for w in hyphen_words:
                wrong_answers.append(w)

        if 'YEAR' in answer_type:
            wrong_answer = [i for i in wrong_answers if len(i)==4]
        if 'MEASUREMENT' in answer_type:            
            wrong_answers = [t2d.convert(str(nlp(i)[0])).lstrip()+' ' + str(correct_answer[-1]) for i in merged]
        if 'MONEY' in answer_type:
            currency = answer[0]
            random_money = [answer[0]+str(num)+' ' +str(correct_answer[-1]) for num in random.sample(range(1, 60), 5)]
            wrong_answers.extend(random_money)
        if 'ADP' in answer_type:
            wrong_answers = [i for i in wrong_answers if i[0]==correct_answer[0].orth_]
    #Remove distractors with part of answer in it
    answer_found=False
    filtered_wrong_answers = []
    
    if ('MEASUREMENT' not in answer_type) and ('NUM' not in answer_type) and ('MONEY' not in answer_type)\
    and ('SCORE' not in answer_type) and ('DATE' not in answer_type):
        print('not measurement, num, date, money')
        for i in wrong_answers:
            answer_found=False
            for word in range(len(correct_answer)):
                if (correct_answer[word].orth_ in ['the','of','a','an','that','to','between', 'and']):
                    answer_found=False
                elif (correct_answer[word].orth_ in str(i)):
                    answer_found=True


            if answer_found==False:
                filtered_wrong_answers.append(i)
                filtered_wrong_answers=[item for item in filtered_wrong_answers if item not in ['a','an','the','that','it','who','what', '',""]]
    else:
        filtered_wrong_answers = wrong_answers
    # if not enough filtered answers, choose first tokens of paragraph up to length of answer
    if len(set(filtered_wrong_answers))<3:

        for article in alt_article_list:
            if len(article)>ans_length:
                filtered_wrong_answers.append(article[:ans_length])
    return (topic, paragraph, qid, question, correct_answer, answer_type, random.sample(list(set(filtered_wrong_answers)),3))
                       

def generate_wrong_answers(in_file,out_file):
    with open(in_file) as f:
        df = json.load(f)
        
    topics = []
    paragraphs = []
    questions = []
    qids = []
    answers = []
    autoq = pd.DataFrame()
    
    data = df['data']
    
    
    for title in range(len(df['data'])):
        for p in range(len(df['data'][title]['paragraphs'])):
            if df['data'][title]['paragraphs'][p]['qas'] == []:
                topics.append(df['data'][title]['title'])
                paragraphs.append(df['data'][title]['paragraphs'][p]['context'])
                questions.append('')
                answers.append('')
                qids.append('')
            else:
                for qa in range(len(df['data'][title]['paragraphs'][p]['qas'])):
                    topics.append(df['data'][title]['title'])
                    paragraphs.append(df['data'][title]['paragraphs'][p]['context'])
                    questions.append(df['data'][title]['paragraphs'][p]['qas'][qa]['question'])
                    qids.append(df['data'][title]['paragraphs'][p]['qas'][qa]['id'])
                    answers.append(df['data'][title]['paragraphs'][p]['qas'][qa]['answers'][0]['text'])
    autoq['topics'] = topics
    autoq['paragraphs'] = paragraphs
    autoq['questions'] = questions
    autoq['id'] = qids
    autoq['answers'] = answers
    #autoq.head()
    
    start = time.time()
    distractors = []
    for i in range(len(autoq)):
        try:
            answer_type = check_answer_type(autoq.loc[i]['answers'])
            topic, paragraph, qid, question, correct_answer, answer_type, wrong_answers = generate_distractor(autoq.loc[i]['topics'], autoq.loc[i]['paragraphs'], autoq.loc[i]['id'],autoq.loc[i]['questions'], autoq.loc[i]['answers'], answer_type)
            distractors.append(wrong_answers)
        except:
            print("error occurred for sample#: " + str(i))
            distractors.append(['NA'])
    autoq['distractors']=distractors
    autoq['distractor_length'] = [1 if (len(autoq.loc[i]['distractors'])==1) else 0 for i in list(autoq.index.values) ]

    print("Progress: processed {} records in {:.2f} minutes".format(len(autoq),(time.time()-start)/60))
    
    new_distractors = []
    for i in range(len(autoq)):
        processed_list = []
        for item in autoq.loc[i]['distractors']:
            if not isinstance(item,str):
                text_version = item.text
                processed_list.append(text_version)
            else:
                processed_list.append(item)
        new_distractors.append(processed_list)
    autoq['new_distractors']=new_distractors
    
    wiki_dict = df['data']

    for record in range(len(autoq)):
        qid = autoq.loc[record]['id']
        for title in range(len(wiki_dict)):
            for p in range(len(wiki_dict[title]['paragraphs'])):
                if wiki_dict[title]['paragraphs'][p]['qas'] == []:
                    continue
                else:
                    for qa in range(len(wiki_dict[title]['paragraphs'][p]['qas'])):
                        if qid==wiki_dict[title]['paragraphs'][p]['qas'][qa]['id']:
                            wiki_dict[title]['paragraphs'][p]['qas'][qa]['distractors'] = autoq.loc[record]['new_distractors']
                    
    df['data']=wiki_dict

    with open(out_file, 'w') as outfile:  
        json.dump(df, outfile)
    
###########################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='wrong_answer_gen.py')
        
    parser.add_argument('--input-dir', type=str, default='./wikipedia_data/wikipedia_squad',
                    help=('Directory to read original squad-formatted file from.'), required=True)
    parser.add_argument('--out-dir', type=str, default='./wikipedia_data/unlabeled_sentences',
                    help=('Directory to write squad-formatted file with distractors to.'), required=True)

    args = parser.parse_args()
    wiki_squad = args.input_dir
    wiki_squad_final = args.out_dir
    
    
    for foldername in os.listdir(wiki_squad):
        
        if not foldername.startswith('.'):
        
            input_subfolder = wiki_squad + foldername
            output_subfolder = wiki_squad_final + foldername
        
            if not os.path.exists(output_subfolder):
                os.mkdir(output_subfolder)
        
            print("Generating wrong answers for files in {} folder...".format(foldername))
        
            for filename in os.listdir(input_subfolder):
                if not filename.startswith('.'):
                
                    input_file = input_subfolder + '/' + filename
                    output_file = output_subfolder + '/' + filename
        
                    generate_wrong_answers(input_file,output_file)