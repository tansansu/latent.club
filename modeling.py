from konlpy.tag import Twitter; pos_tagger = Twitter()
import pandas as pd

# Import Training Dataset
train = pd.read_excel('/Users/tansansu/Google Drive/Python/latent_info/sample_data/sample_estate.xlsx')
train = train[train['result'].notnull()][['title', 'result']]
train['result'] = train['result'].astype(int).astype(str)
# Data cleansing
train.loc[train['result'] == '1', 'result'] = 'Y'
train.loc[train['result'] == '0', 'result'] = 'N'
# Creating labeled list
train_result = train['result'].tolist()

# Tokenize
def tokenizer(sentence):
    temp = ['/'.join(t) for t in pos_tagger.pos(sentence, norm=True, stem=True)]
    # only Verb, Noun, Adjective
    result = [x for x in temp \
    if re.match(r'([가-힣]+/Noun)|([가-힣]+/Verb)|([가-힣]+/Adjective)', x) != None]
            
    return(result)

words = train['title'].apply(tokenizer).tolist()
tokens = [t for l in words for t in l if t]
# Making Training data set
training = [(t, r) for t, r in zip(words, train_result)]

import nltk
text = nltk.Text(tokens, name='NMSC')

def term_exists(doc):
 return {'exists({})'.format(word): (word in set(doc)) for word in text.vocab().keys()}

train_xy = [(term_exists(t), r) for t, r in training]

classifier = nltk.NaiveBayesClassifier.train(train_xy)
# classifier
# print(nltk.classify.accuracy(classifier, train_xy))
# classifier.show_most_informative_features(20)
# classifier.classify(term_exists(words[1]))

# Savting the model
import pickle

f = open('/Users/tansansu/Google Drive/Python/latent_info/model_nb.pickle', 'wb')
pickle.dump(classifier, f)
f.close()


