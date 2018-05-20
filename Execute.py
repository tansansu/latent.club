# 2018.01.01

import json
import sqlite3
import pandas as pd
import logging
import sys
sys.path.insert(0, 'latent_info/')
sys.path.append('/home/revlon/Codes/Telegram_Bot/')
sys.path.append('/Users/tansansu/Google Drive/Python/Telegram_Bot/')
#sys.path.append('/home/jar/Codes/Telegram_Bot/')
import F_common 
import F_Classifier
from datetime import datetime
from TelegramBot import TelegramBot


# 함수: 게시판 md 파일 생성 작업 실행
def execute_md(subject_key, size):
    # db파일에서 게시글 리스트 추출
    conn = sqlite3.connect('db/board.db')
    if subject_key == 'stock': ## 주식 게시판에서 코인 글은 제외
        query = 'select site, title, article_link, date_time, view_num, reply_num from \
        (select site, title, article_link, date_time, view_num, reply_num, article_id from \
        %s where result = "Y" order by date_time desc limit %d) where article_id not in \
        (select article_id from coin order by date_time desc limit %d) limit %d;' % \
        (subject[subject_key], size, size, size)
    else:
        query = 'select site, title, article_link, date_time, view_num, reply_num from \
        %s where result = "Y" order by date_time desc limit %d;' % (subject[subject_key], size)
    df = pd.read_sql(query, conn)
    conn.close()
    ## 중복글 제거(제목)
    df.drop_duplicates('title', inplace=True)
    ### 데이터 프레임을 5개 페이지로 나누어서 md파일(페이지)로 만들기
    #directory = '/Users/tansansu/Google Drive/blog/latent-info/content/' + subject[subject_key]
    directory = '/home/revlon/Codes/Web/hugo_latent-info/content/' + subject[subject_key]
    for i in range(7):
        F_common.to_md(df.iloc[30*i:30*(i+1)], subject_key, directory, i+1)
    

if __name__ == '__main__':
    # 로깅
    logging.basicConfig(filename='./log/test.log',level=logging.WARNING)
    logging.info('=========================================')

    # 기준 정보
    subject = {'부동산':'estate', '찌라시':'tabloid', '주식':'stock', \
    '경제':'economy', '트윗':'tweet', '가상화폐':'coin'}
    site = ['클리앙', '딴지일보', '루리웹', '엠팍', '오유', '이토렌트', \
    '뽐뿌', 'SLR', '82cook', '인벤', 'DVD프라임']

    # 코드 동작 시간 측정용
    start_time = datetime.now().replace(microsecond=0)
    # 로깅
    log = 'Start_time: ' + str(datetime.now().replace(microsecond=0)) + '\n'
    print(log)
    logging.info(log)

    # 특정 사이트만 돌리고 싶은 경우
    try:
        if sys.argv[1]:
            site = [sys.argv[1]]
    except:
        pass

    for j in subject:
        # log 메세지 생성
        log += '[ %s ]\n' % j
        # 검색 url 불러오기
        with open('links/' + subject[j] + '.json','r') as f:
            url = json.load(f)

        for i, s in enumerate(site):
            try:
                print(j + ' | ' + s)
                ## article 가져오기
                result = F_common.scrapper(s, url)
                print(result.shape)
                logging.debug(result.shape)
                if result.shape[0] >= 1:
                    ### 19금 글 제거
                    result = F_common.adult_filter(result)
                    ### 머신러닝 분류(트윗 주제는 제목의 글자포함 여부만 필터링함)
                    if j == '트윗':
                        result = F_common.tweet_name_filter(result)
                    elif j == '가상화폐':
                        result = F_common.coin_name_filter(result)
                    else:
                        result = F_Classifier.predict_Y(result, subject[j])
                    ### DB에 게시글 저장
                    article_count = F_common.store_db(subject[j], s, result)
                else:
                    article_count = 0
                log += '-%d %s: %d개 수집\n' % (i+1, s, article_count)
            except Exception as e:
                print(e)
                logging.error(e)
            ## 프린트 메시지
            print('%s - %s 완료' % (j, s))
            logging.debug('%s - %s 완료' % (j, s))
        log += '\n'
        # md 파일 생성
        execute_md(j, size=300)
    end_time = datetime.now().replace(microsecond=0)
    # log에 동작 시간 추가
    message = '업데이트 동작 시간: ' + str(end_time - start_time)
    log += message; logging.info(message)

    # 게시물 수집 log 텔레그램으로 전송
    TelegramBot().log_to_me(log)
