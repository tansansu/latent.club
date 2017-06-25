# 2017.06.25

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


def predict_Y(dataframe, subject):
    words = dataframe['title'].apply(tokenizer).tolist()
    # loading the model & text sets
    with open('db/nb_model_'+ subject +'.pickle', 'rb') as f:
        model = pickle.load(f)
    with open('db/nb_text_' + subject + '.pickle', 'rb') as f:
        text = pickle.load(f)
    # Prediction
    dataframe['result'] = [model.classify(term_exists(text, word)) for word in words]
    
    return(dataframe)

    