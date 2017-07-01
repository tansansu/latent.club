# 2017.04.08

from konlpy.tag import Twitter; pos_tagger = Twitter()
import pandas as pd
import random
import re

# Choose the subject
subject = 'coin'

# Import Training Dataset
filename = 'sample_' + subject + '.xlsx'
filename
directory = '/Users/tansansu/Google Drive/Python/latent_info/sample_data/'
raw = pd.read_excel(directory + filename)
raw = raw[['title', 'result']]
# raw['result'] = raw['result'].astype(int).astype(str)
raw.head()
# Data cleansing
raw.loc[raw['result'] == 1, 'result'] = 'Y'
raw.loc[(raw['result'] == 0) | (raw['result'].isnull()), 'result'] = 'N'


# Tokenize
def tokenizer(sentence):
    temp = ['/'.join(t) for t in pos_tagger.pos(sentence, norm=True, stem=True)]
    # only Verb, Noun, Adjective
    result = [x for x in temp \
    if re.match(r'([가-힣]+/Noun)|([가-힣]+/Verb)|([가-힣]+/Adjective)', x) != None]
            
    return(result)

# Making Training data set
## sampling
train_idx = random.sample(range(len(raw)), round(len(raw)*.6))
train = raw.iloc[train_idx]
test = raw[~raw.index.isin(train_idx)]
# Creating labeled list
train_result = train['result'].tolist()
test_result = test['result'].tolist()
# Extracting words and tokens
train_words = train['title'].apply(tokenizer).tolist()
test_words = test['title'].apply(tokenizer).tolist()
train_tokens = [t for l in train_words for t in l if t]
test_tokens = [t for l in test_words for t in l if t]

training = [(t, r) for t, r in zip(train_words, train_result)]
testing = [(t, r) for t, r in zip(test_words, train_result)]

import nltk
text = nltk.Text(train_tokens, name='NMSC')
len(text.vocab())
len(set(text))
selected_word = [w for w in text.vocab()]

def term_exists(doc):
    return {'exists({})'.format(word): (word in set(doc)) for word in selected_word}

train_xy = [(term_exists(t), r) for t, r in training]
test_xy = [(term_exists(t), r) for t, r in testing]

classifier = nltk.NaiveBayesClassifier.train(train_xy)
classifier
# 성능 확인
print(nltk.classify.accuracy(classifier, train_xy))
print(nltk.classify.accuracy(classifier, test_xy))
classifier.show_most_informative_features(20)
# classifier.classify(term_exists(test_words[20]))

# Savting the model
import pickle

def export_model(subject):
    f = open('db/nb_model_' + subject + '.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()

    with open('db/nb_text_' + subject + '.pickle', 'wb') as f:
        pickle.dump(text, f)


export_model(subject)

