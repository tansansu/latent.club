 # 2017.04.09

import json
import sqlite3
import pandas as pd
import sys
sys.path
sys.path.insert(0, 'latent_info/')
import F_common
import F_Classifier
import datetime


# 함수: 게시판 md 파일 생성 작업 실행
def execute_md(subject_key):
    ## md파일 생성
    ### db파일에서 게시글 리스트 추출
    count = '300'
    if (subject_key == '경제') | (subject_key == '찌라시'):
        count = '700'
    with sqlite3.connect('db/board.db') as conn:
        query = 'select site, title, article_link, date_time from ' + subject[subject_key] + \
        ' order by date_time desc limit ' + count + ';'
        df = pd.read_sql_query(query, conn)
    ### 날짜/시간 역순으로 ordering
    # df.sort_values('date_time', ascending=False, inplace=True)

    ### 머신러닝 분류
    df = F_Classifier.predict_Y(df, subject[subject_key])
    df = df[df['result'] == 'Y']
    
    ## 중복글 제거(제목)
    df.drop_duplicates('title', keep='first', inplace=True)
    ## 19금 글 제거
    df = df[~df['title'].str.contains('19')]

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



# 콘텐츠 업데이트
subject = {'부동산':'estate', '찌라시':'tabloid', '주식':'stock', '경제':'economy'}

site_link = {'클리앙':'clien', '딴지일보':'ddan', \
    '루리웹':'ruli', '엠팍':'mlb', '웃대':'HuU', '이토렌트':'eto', '뽐뿌':'ppom', \
    'SLR':'slr', '82cook':'82cook'}

log = ''
# 코드 동작 시간 측정용
start_time = datetime.datetime.now().replace(microsecond=0)

for j in subject:
    # log 메세지 생성
    log += '[ %s ]\n' % j
    # 검색 url 불러오기
    with open('links/' + subject[j] + '.json','r') as f:
        url = json.load(f)
    
    for s in site_link:
        try:
            ## article 가져오기
            result = F_common.scrapper(s, url[site_link[s]])
            ## DB에 게시글 저장
            article_count = F_common.store_db(subject[j], s, result)
            log += '-%s: %d개 수집\n' % (s, article_count)
        except:
            pass
        # 프린트 메시지
        print('%s - %s 완료' % (j, s))
    log += '\n'

    execute_md(j)
end_time = datetime.datetime.now().replace(microsecond=0)
# log에 동작 시간 추가
log += '업데이트 동작 시간: ' + str(end_time - start_time)

# 게시물 수집 log 텔레그램으로 전송
F_common.noti_to_telegram(log)
