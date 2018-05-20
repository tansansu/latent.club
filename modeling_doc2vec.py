# 2017.04.08

from konlpy.tag import Twitter; pos_tagger = Twitter()
import pandas as pd
import random
import re

# Choose the subject
subject = 'tabloid'

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
testing = [(t, r) for t, r in zip(test_words, test_result)]

import nltk
text = nltk.Text(train_tokens, name='NMSC')
len(text.vocab())
len(set(text))
selected_word = [w for w in text.vocab()]


from collections import namedtuple
TaggedDocument = namedtuple('TaggedDocument', 'words tags')

tagged_train_docs = [TaggedDocument(d, [c]) for d, c in training]
tagged_test_docs = [TaggedDocument(d, [c]) for d, c in testing]
len(tagged_test_docs)

from gensim.models import doc2vec

config = {
    'size': 300,  # 300차원짜리 벡터스페이스에 embedding
    'alpha': 0.025, 
    'min_alpha': 0.025, 
    'seed': 1234
}
model = doc2vec.Doc2Vec(**config)
model.build_vocab(tagged_train_docs)
 # Train document vectors!
for epoch in range(10):
    model.train(tagged_train_docs, total_examples=700000, epochs=1)
    model.alpha -= 0.002  # decrease the learning rate
    model.min_alpha = model.alpha



# Savting the model
import pickle

def export_model(subject):
    f = open('db/nb_model_' + subject + '.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()

    with open('db/nb_text_' + subject + '.pickle', 'wb') as f:
        pickle.dump(text, f)


export_model(subject)

