import json
import flask
import numpy as np
import pandas as pd
import random
from os import listdir, scandir
from os.path import isfile, join

app = flask.Flask(__name__)
app.secret_key = "super secret key"
app.config["DEBUG"] = True

# Loading the data
mypath = "./for_autoq"
subfolders = [f.path for f in scandir(mypath) if f.is_dir() ]
topic_dict = {}
# get the names of the files in each folder
for sub in subfolders:
    onlyfiles = [f for f in listdir(sub) if isfile(join(sub, f))]
    for file in onlyfiles:
        try:
            df = pd.read_json(str(sub+"/"+file))
            for entry in range(0, len(df['data'])):
                topic_dict[df['data'][entry]['title']] = str(sub+"/"+file)
        except:
            continue
topic_list = list(topic_dict.keys())
topic_list.sort()


# home page for site
@app.route('/', methods=['GET', 'POST'])
def home():
    flask.session['Correct'] = 0
    flask.session['Incorrect'] = 0
    flask.session['Blank'] = 0
    flask.session['id_list'] = []
    return flask.render_template("index.html")

# home page for site
@app.route('/topic_select', methods=['GET', 'POST'])
def topic():
    return flask.render_template("topic_select.html", topic_list = topic_list)

@app.route('/about_us', methods=['GET'])
def about_us():
    return flask.render_template("about_us.html")

@app.route('/our_project', methods=['GET'])
def our_project():
    return flask.render_template("our_project.html")

@app.route('/article', methods=['GET', 'POST'])
def api_article():
# when a particular topic has been selected
    if flask.request.method == 'POST':
        # Then get the data from the form
        title = flask.request.form['topic_select']

    else:
        if flask.session.get('title', None) != None:
            title = flask.session.get('title')
    article_title = title.title()

# STILL NEED TO ADD VALIDATION
    df_art = pd.read_json(topic_dict[title])

# determine the number in the json file for this article
    indicator = False
    topic = 0
    while indicator == False:
        if df_art.data.iloc[topic]['title'] == title:
            indicator = True
        else:
            topic += 1
# create article context
    article = []
    for paragraph in range(0, len(df_art.data.iloc[topic]['paragraphs'])):
        article.append(df_art.data.iloc[topic]['paragraphs'][paragraph]['context'])
#   cannot store entire article in the session variables because too large

    radio_buttons = ['answer_0', 'answer_1', 'answer_2', 'answer_3', 'answer_4']
    id_list = flask.session.get("id_list")
    qs = {}
    q_achoices = {}
    q_correcta = {}
    answer_choices = ['Answer 1', 'Answer 2', 'Answer 3'] # stand-in for actual data
    for p in range(0, len(df_art['data'].iloc[topic]['paragraphs'])):
        if df_art['data'].iloc[topic]['paragraphs'][p]['qas'] != []:
            for q in range(0, len(df_art['data'].iloc[topic]['paragraphs'][p]['qas'])):
                if len(df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['distractors']) > 2:
                # if len(answer_choices) > 2:
                    qs[df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['id']] = df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['question']
                    q_correcta[df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['id']] = df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['answers'][0]['text']
                    answer_choices = df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['distractors'] + [df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['answers'][0]['text']]
                    # answer_choices = ['Answer 1', 'Answer 2', 'Answer 3'] # stand-in for actual data
                    # answer_choices.append(df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['answers'][0]['text'])
                    random.shuffle(answer_choices)
                    q_achoices[df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['id']] = answer_choices
    # need to find 5 random questions
    # first figure out which questions are available
    avail_qs = list(set(qs.keys()) - set(id_list))
    if len(avail_qs) >= 5:
        current_qs = random.sample(avail_qs, 5)
    else:
        current_qs = avail_qs
    id_list += current_qs

    # check to see which questions are still available
    if len(set(qs.keys()) - set(id_list)) > 0:
        more_qs = "yes"
    else:
        more_qs = "no"

    flask.session['questions'] = qs
    flask.session['id_list'] = id_list
    flask.session['current_qs'] = current_qs
    flask.session['topic'] = topic
    flask.session['article_title'] = article_title
    flask.session['title'] = title
    flask.session['q_correcta'] = q_correcta
    flask.session['more_qs'] = more_qs

    return flask.render_template("article.html", title = article_title, article = article, numbering = list(range(len(current_qs))), id_list = current_qs, questions = qs, q_achoices = q_achoices, radio_buttons = radio_buttons)

    # return flask.render_template("article.html", title = article_title, article = article)

@app.route('/random', methods=['GET', 'POST'])
def api_random():
# when a particular topic has been selected
    if flask.request.method == 'GET':
        # Then get the data from the form
        title = random.sample(topic_list, 1)[0]
        article_title = title.title()
# STILL NEED TO ADD VALIDATION
    df_art = pd.read_json(topic_dict[title])

# determine the number in the json file for this article
    indicator = False
    topic = 0
    while indicator == False:
        if df_art.data.iloc[topic]['title'] == title:
            indicator = True
        else:
            topic += 1
# create article context
    article = []
    for paragraph in range(0, len(df_art.data.iloc[topic]['paragraphs'])):
        article.append(df_art.data.iloc[topic]['paragraphs'][paragraph]['context'])
#   cannot store entire article in the session variables because too large

    radio_buttons = ['answer_0', 'answer_1', 'answer_2', 'answer_3', 'answer_4']
    id_list = flask.session.get("id_list")
    qs = {}
    q_achoices = {}
    q_correcta = {}
    answer_choices = ['Answer 1', 'Answer 2', 'Answer 3'] # stand-in for actual data
    for p in range(0, len(df_art['data'].iloc[topic]['paragraphs'])):
        if df_art['data'].iloc[topic]['paragraphs'][p]['qas'] != []:
            for q in range(0, len(df_art['data'].iloc[topic]['paragraphs'][p]['qas'])):
                if len(df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['distractors']) > 2:
                # if len(answer_choices) > 2:
                    qs[df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['id']] = df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['question']
                    q_correcta[df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['id']] = df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['answers'][0]['text']
                    answer_choices = df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['distractors'] + [df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['answers'][0]['text']]
                    # answer_choices = ['Answer 1', 'Answer 2', 'Answer 3'] # stand-in for actual data
                    # answer_choices.append(df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['answers'][0]['text'])
                    random.shuffle(answer_choices)
                    q_achoices[df_art['data'].iloc[topic]['paragraphs'][p]['qas'][q]['id']] = answer_choices
    # need to find 5 random questions
    avail_qs = list(set(qs.keys()) - set(id_list))
    if len(avail_qs) >= 5:
        current_qs = random.sample(avail_qs, 5)
    else:
        current_qs = avail_qs
    id_list += current_qs

    if len(set(list(qs.keys())) - set(id_list)) > 0:
        more_qs = "yes"
    else:
        more_qs = "no"

    flask.session['questions'] = qs
    flask.session['id_list'] = id_list
    flask.session['current_qs'] = current_qs
    flask.session['topic'] = topic
    flask.session['article_title'] = article_title
    flask.session['title'] = title
    flask.session['q_correcta'] = q_correcta
    flask.session['more_qs'] = more_qs

    return flask.render_template("article.html", title = article_title, article = article, numbering = list(range(len(qs))), id_list = current_qs, questions = qs, q_achoices = q_achoices, radio_buttons = radio_buttons)

@app.route('/check_answers', methods=['GET', 'POST'])
def api_grade():
    article_title = flask.session.get('article_title', None)
    title = flask.session.get('title', None)
# import list of questions and answers
    current_qs = flask.session.get('current_qs', None)
    q_questions = flask.session.get('questions', None)
    q_correcta = flask.session.get('q_correcta', None)
# Then need to recreate the article - cannot pass through session data because too large
    df_art = pd.read_json(topic_dict[title])

# determine the number in the json file for this article
    indicator = False
    topic = 0
    while indicator == False:
        if df_art.data.iloc[topic]['title'] == title:
            indicator = True
        else:
            topic += 1
# create article context
    article = []
    for paragraph in range(0, len(df_art.data.iloc[topic]['paragraphs'])):
        article.append(df_art.data.iloc[topic]['paragraphs'][paragraph]['context'])
# Bring in users answers
    numbering = list(range(len(current_qs)))
    user_answers = {}
    radio_buttons = {}
    for q in numbering:
        a_num = "answer_"+str(q)
        try:
            answer = flask.request.form[a_num]
        except:
            answer = "Not Answered"
        user_answers[current_qs[q]] = answer
        radio_buttons[current_qs[q]] = "q_" + str(q)
# check if user answer is correct
    correct = {}
    if flask.session.get("Correct", None) == None:
        num_corr = 0
    else:
        num_corr = flask.session.get("Correct")
    if flask.session.get("Incorrect", None) == None:
        num_wrong = 0
    else:
        num_wrong = flask.session.get("Incorrect")
    if flask.session.get("Blank", None) == None:
        num_blank = 0
    else:
        num_blank = flask.session.get("Blank")
    answer_color = {}
    for q in current_qs:
        if (user_answers[q] == q_correcta[q]):
            correct[q] = "Correct"
            answer_color[q] = "correct"
            num_corr += 1
        elif user_answers[q] == "Not Answered":
            correct[q] = "Not Answered"
            answer_color[q] = "blank"
            num_blank += 1
        else:
            correct[q] = "Incorrect"
            answer_color[q] = "incorrect"
            num_wrong += 1
    if flask.session['more_qs'] == "yes":
        render = "check_answers.html"
    else:
        render = "check_no_more_qs.html"

    flask.session['Correct'] = num_corr
    flask.session['Incorrect'] = num_wrong
    flask.session['Blank'] = num_blank

    return flask.render_template(render, article = article, answers = user_answers, title = article_title, questions = current_qs, q_list = q_questions, numbering = numbering, correct = correct, answer_color = answer_color, correct_answers = q_correcta, radio_buttons = radio_buttons)
    # return flask.render_template("check_answers.html", article = article)

@app.route('/score', methods=['GET', 'POST'])
def api_score():
    num_corr = flask.session.get("Correct", None)
    num_wrong = flask.session.get("Incorrect", None)
    num_blank = flask.session.get("Blank", None)

    radio_buttons = ['q_0', 'q_1', 'q_2', 'q_3', 'q_4']
    bad_qs = []
    for a in radio_buttons:
        try:
            bad_q = flask.request.form[a]
            bad_qs.append(bad_q)
        except:
            # bad_qs.append("WHY")
            continue
    flask.session['Bad_q'] = bad_qs

    return flask.render_template("score_card.html", num_corr = num_corr, num_wrong = num_wrong, num_blank = num_blank)

@app.route('/feedback', methods=['GET', 'POST'])
def api_feedback():
    bad_qs = flask.session.get("Bad_q", "Nothing here")

    return flask.render_template("feedback.html", bad_qs = bad_qs)


if __name__ == '__main__':
    app.run()
