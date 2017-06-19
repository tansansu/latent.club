# 2017.06.15

import pandas as pd


# 제목에 트윗이 표시된 것만 추출하는 함수
def tweet_name(dataframe):
   return(dataframe[dataframe['title'].str.contains('트윗.') | dataframe['title'].str.contains('트위터.')])

