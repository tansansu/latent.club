 # 2017.05.07

import json
import sqlite3
import pandas as pd
import sys
sys.path
sys.path.insert(0, 'latent_info/')
sys.path.append('/home/jar/Codes/Telegram_Bot/')
import F_common 
import F_Classifier
from datetime import datetime
from TelegramBot import TelegramBot


# 함수: 게시판 md 파일 생성 작업 실행
def execute_md(subject_key):
    ## md파일 생성
    ### db파일에서 게시글 리스트 추출
    with sqlite3.connect('db/board.db') as conn:
        query = 'select site, title, article_link, date_time from ' + subject[subject_key] + \
        ' where result = "Y" order by date_time desc limit 185;'
        df = pd.read_sql_query(query, conn)
    ## 중복글 제거(제목)
    df.drop_duplicates('title', keep='first', inplace=True)

    ### 데이터 프레임을 3개 페이지로 나누기
    df_1 = df.iloc[:60]
    df_2 = df.iloc[60:120]
    df_3 = df.iloc[120:180]

    ### 각각의 데이터프레임을 3개의 md파일(페이지)로 만들기
    # directory = '/Users/tansansu/Google Drive/blog/latent-info/content/' + subject[subject_key]
    directory = '/home/jar/web/hugo_latent-info/content/' + subject[subject_key]
    F_common.to_md(df_1, subject_key, directory, 1)
    F_common.to_md(df_2, subject_key, directory, 2)
    F_common.to_md(df_3, subject_key, directory, 3)


# 기준 정보
subject = {'부동산':'estate', '찌라시':'tabloid', '주식':'stock', '경제':'economy'}
site = ['클리앙', '딴지일보', '루리웹', '엠팍', '웃대', '이토렌트', '뽐뿌', 'SLR', '82cook']

log = ''
# 코드 동작 시간 측정용
start_time = datetime.now().replace(microsecond=0)

for j in subject:
    # log 메세지 생성
    log += '[ %s ]\n' % j
    # 검색 url 불러오기
    with open('links/' + subject[j] + '.json','r') as f:
        url = json.load(f)
    
    for s in site:
        try:
            print(j + ' | ' + s)
            ## article 가져오기
            result = F_common.scrapper(s, url)
            print(result.shape)
            if result.shape[0] >= 1:
                ## 19금 글 제거
                result = result[~result['title'].str.contains('19')]
                ### 머신러닝 분류
                result = F_Classifier.predict_Y(result, subject[j])
                ## DB에 게시글 저장
                article_count = F_common.store_db(subject[j], s, result)
            else:
                article_count = 0
            log += '-%s: %d개 수집\n' % (s, article_count)
        except Exception as e:
            print(e)
        # 프린트 메시지
        print('%s - %s 완료' % (j, s))
    log += '\n'
    # md 파일 생성
    execute_md(j)
end_time = datetime.now().replace(microsecond=0)
# log에 동작 시간 추가
log += '업데이트 동작 시간: ' + str(end_time - start_time)

# 게시물 수집 log 텔레그램으로 전송
TelegramBot().log_to_me(log)
