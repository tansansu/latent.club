# 2017.02.26

from konlpy.tag import Twitter; pos_tagger = Twitter()
import pandas as pd
import pickle
import nltk
import re


# Tokenizing Fuction
def tokenizer(sentence):
    temp = ['/'.join(t) for t in pos_tagger.pos(sentence, norm=True, stem=True)]
    # only Verb, Noun, Adjective
    result = [x for x in temp \
    if re.match(r'([가-힣]+/Noun)|([가-힣]+/Verb)|([가-힣]+/Adjective)', x) != None]
            
    return(result)


# 단어 존재 여부 확인
def term_exists(text, doc):
    return {'exists({})'.format(word): (word in set(doc)) for word in text.vocab().keys()}


def predict_Y(dataframe):
    words = dataframe['title'].apply(tokenizer).tolist()
    
    # loading the model & text sets
    f = open('/Users/tansansu/Google Drive/Python/latent_info/model_nb.pickle', 'rb')
    model = pickle.load(f)
    f.close()
    f = open('/Users/tansansu/Google Drive/Python/latent_info/nb_text.pickle', 'rb')
    text = pickle.load(f)
    f.close()
    
    
    # Prediction
    dataframe['result'] = ''
    for i in range(len(words)):
        dataframe.loc[i, 'result'] = model.classify(term_exists(text, words[i]))
    
    return(dataframe)
    
    