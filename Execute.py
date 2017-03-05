# 2017.03.01

import pickle
import os
import sqlite3
import pandas as pd
import time
import sys
sys.path
sys.path.insert(0, 'latent_info/')
import F_common
import F_Classifier


# 링크 저장
# f = open('/Users/tansansu/Google Drive/Python/latent_info/links/estate_slr.pickle', 'wb')
# pickle.dump(slr_url, f)
# f.close()


# 함수: 게시판 md 파일 생성
def execute_md(subject_key):
    ## md파일 생성
    ### db파일에서 게시글 리스트 추출
    with sqlite3.connect('/Users/tansansu/Google Drive/Python/latent_info/board.db') as conn:
        query = 'select site, title, article_link, date_time from ' + subject[subject_key] + \
        ' order by date_time desc limit 300;'
        df = pd.read_sql_query(query, conn)
    ### 날짜/시간 역순으로 ordering
    df.sort_values('date_time', ascending=False, inplace=True)

    ### 머신러닝 분류
    df = F_Classifier.predict_Y(df)
    df = df[df['result'] == 'Y']

    ### 데이터 프레임을 3개 페이지로 나누기
    df_1 = df.iloc[:60]
    df_2 = df.iloc[60:120]
    df_3 = df.iloc[120:180]

    ### 각각의 데이터프레임을 3개의 md파일(페이지)로 만들기
    directory = '/Users/tansansu/Google Drive/blog/latent-info/content/' + subject[subject_key]
    F_common.to_md(df_1, subject_key, directory, 1)
    F_common.to_md(df_2, subject_key, directory, 2)
    F_common.to_md(df_3, subject_key, directory, 3)



subject = {'부동산':'estate'}, '찌라시':'tabloid'}

site_link = {'클리앙':'clien', '딴지일보':'ddan', \
    '루리웹':'ruli', '엠팍':'mlb', '웃대':'HuU', '이토렌트':'Eto', '뽐뿌':'ppom', \
    'SLR':'slr'}

for j in subject:
    for s in site_link:
        directory = '/Users/tansansu/Google Drive/Python/latent_info/links/'
        with open(directory + subject[j] +'_' + site_link[s] + '.pickle','rb') as f:
            url = pickle.load(f)
    
        try:
            ## Get articles
            result = F_common.scrapper(s, url)
            ## DB에 게시글 저장
            F_common.store_db(subject[j], s, result)
        except:
            pass

    execute_md(j)

