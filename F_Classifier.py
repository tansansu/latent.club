# 2017.06.25

from konlpy.tag import Twitter; pos_tagger = Twitter()
import pickle
import re


class Classifier:
    def __init__(self, subject):
        # loading the model & text sets
        with open('db/nb_model_' + subject + '.pickle', 'rb') as f:
            self.model = pickle.load(f)
        with open('db/nb_text_' + subject + '.pickle', 'rb') as f:
            self.text = pickle.load(f)

    # Tokenizing Fuction
    @staticmethod
    def tokenizer(sentence):
        temp = ['/'.join(t) for t in pos_tagger.pos(sentence, norm=True, stem=True)]
        # only Verb, Noun, Adjective
        return [x for x in temp if re.match(r'([가-힣]+/Noun)|([가-힣]+/Verb)|([가-힣]+/Adjective)', x) is not None]

    # 단어 존재 여부 확인
    @staticmethod
    def term_exists(text, doc):
        return {'exists({})'.format(word): (word in set(doc)) for word in text.vocab().keys()}

    def predict_Y(self, df):
        words = df['title'].apply(self.tokenizer).tolist()
        #print("words cnt: %d" % len(words))
        # Prediction
        df.loc[:, 'result'] = [self.model.classify(self.term_exists(self.text, word)) for word in words]
        return df
