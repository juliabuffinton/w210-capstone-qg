# AutoQ: Improving reading comprehension through automatic question generation
Repository for Question Generation project, W210 Capstone for UCB MIDS.
Julia Buffinton, Saurav Datta, Joanna Huang, Kathryn Plath

## About Our Project
AutoQ is the first free web app with automatically generated reading comprehension questions targeted to English language learners. Our product utilizes state of the art machine learning and natural language processing techniques to create a vast and topical collection of multiple-choice questions that mimic English-language exam formats. We currently offer over 100,000 practice questions on over 10,000  Wikipedia articles.

[Our site](https://autoq-2019.herokuapp.com/) is designed to help improve reading comprehension for English-language learners or for anyone looking to study up on a new topic. Starting with the articles from Wikipedia, we have developed algorithms to produce reading comprehension questions designed to mimic the style of questions seen on the TOEFL exam. Improving reading comprehension is achieved from practice on new material. 

## Do it Yourself
We employed several techniques to achieve this result. The below instructions walk through our approach. Input and output folders can be updated from within the scripts.

### 1. Preprocess Wikipedia articles
Raw text to Wikipedia articles was obtained from [Wikimedia dumps](https://dumps.wikimedia.org/). For the rest of the pipeline, it shoudl be formatted the same was as SQuAD datasets.

From this directory, run the preprocessing script to break up the Wikipedia articles into paragraphs and save them into the `wikipedia_squad` folder.

``` sh preprocess.sh```

### 2. Select relevant sentences to query
Using the paragraphs from the Wikipedia articles, we identify the most “important” sentences to ask questions about. In general, the first and last sentences of each paragraphs often introduce key information or summarize information in the paragraph, so we examine those. We assume that words that appear most frequently are most important (and likely good indicators of the main topic), and therefore the most “important” sentences contain these frequent words.

From this directory, run the sentence selection script to select important sentences and save them, labeled with their location (in `labeled_sentences`) and unlabled for question generation (in `unlabeled_sentences`).

``` sh sentence_selection.sh```

### 3. Question Generation
We then feed these important sentences into our Question Generation model, an attention-based bidirectional LSTM, inspired by Du et al.'s 2017 paper, [Learning to Ask: Neural Question Generation for Reading Comprehension](https://arxiv.org/abs/1705.00106). We implement it using Torch on top of the [Open Neural Machine Translation](http://opennmt.net/) framework. Our approach is adapted from [GenerationQ](https://github.com/drewserles/GenerationQ).

From this directory, run the question generation script to generate questions for the important sentences, save them in the `questions` folder, and add them back to the SQuAD-formatted Wikipedia articles (done with a call to `add_questions.py`, overwriting the files in `wikipedia_squad`).

``` sh question_generation.sh```

### 3. Question Answering
To make these questions useful as a tool for reading comprehension, we must also generate their answers, so users can compare their results. We generate these also with a  bidirectional LSTM, which we chose for its relative simplictiy and competitive performance on our validation set. Our implementation was modelled after part of Facebook’s 2017 paper [Reading Wikipedia to Answer Open-Domain Questions](https://arxiv.org/abs/1704.00051), and [implemented via PyTorch](https://github.com/facebookresearch/DrQA).

From this directory, run the question answering script to generate answers to our questions, save them in the `answers` folder, and add them back to the SQuAD-formatted Wikipedia articles (done with a call to `add_answers.py`, saving the files in `wikipedia_squad_w_answers`).

``` sh question_answering.sh```
