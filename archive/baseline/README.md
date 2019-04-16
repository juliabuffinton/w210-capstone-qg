# Testing TF NMT model as a baseline

1. Visit and clone: `git clone https://github.com/tensorflow/nmt`
2. Make sure you have the correct version of tensorflow installed for the version you'd like to clone: 
    1. Use `git checkout -b [branch-name]` to navigate between branches as needed
    2. Potential branches are `tf-1.2` and `tf-1.4`
3. Follow the instructions at `https://github.com/tensorflow/nmt/tree/master#hands-on--lets-train-an-nmt-model` 
to run the demo (instructions repeated here). It'll download files and run the model.

Let's train our very first NMT model, translating from Vietnamese to English! The entry point of our code is nmt.py.

We will use a small-scale parallel corpus of TED talks (133K training examples) for this exercise. All data we used here can be found at: https://nlp.stanford.edu/projects/nmt/. We will use tst2012 as our dev dataset, and tst2013 as our test dataset.

Run the following command to download the data for training NMT model:
```nmt/scripts/download_iwslt15.sh /tmp/nmt_data```

Run the following command to start the training:

```mkdir /tmp/nmt_model
python -m nmt.nmt \
    --src=vi --tgt=en \
    --vocab_prefix=/tmp/nmt_data/vocab  \
    --train_prefix=/tmp/nmt_data/train \
    --dev_prefix=/tmp/nmt_data/tst2012  \
    --test_prefix=/tmp/nmt_data/tst2013 \
    --out_dir=/tmp/nmt_model \
    --num_train_steps=12000 \
    --steps_per_stats=100 \
    --num_layers=2 \
    --num_units=128 \
    --dropout=0.2 \
    --metrics=bleu
```
     
 4. If that works, use the data files found in `baseline/data` to run (from the top directory in the `nmt` repo!!) it on our own text:
 
 ```mkdir [PATH_TO_W210_REPO]/baseline/model/
python -m nmt.nmt \
    --src=para --tgt=ques \
    --vocab_prefix=[PATH_TO_W210_REPO]/baseline/data/vocab  \
    --train_prefix=[PATH_TO_W210_REPO]/baseline/data/train \
    --dev_prefix=[PATH_TO_W210_REPO]/baseline/data/dev  \
    --test_prefix=[PATH_TO_W210_REPO]/baseline/data/test \
    --out_dir=[PATH_TO_W210_REPO]/baseline/model/ \
    --num_train_steps=16000 \
    --steps_per_stats=500 \
    --num_layers=2 \
    --num_units=600 \
    --dropout=0.3 \
    --metrics=bleu
```
 
