# 2018.01.01

import json
import sqlite3
import pandas as pd
#import logging
import sys
sys.path.insert(0, 'latent_info/')
sys.path.append('/home/revlon/Codes/Telegram_Bot/')
sys.path.append('/Users/tansansu/Google Drive/Python/Telegram_Bot/')
#sys.path.append('/home/jar/Codes/Telegram_Bot/')
import F_common 
import F_Classifier
from datetime import datetime
from TelegramBot import TelegramBot


# 사이트별로 연속적으로 실행
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
    # 기준 정보
    subject = {'부동산':'estate', '찌라시':'tabloid', '주식':'stock', \
    '경제':'economy', '트윗':'tweet', '가상화폐':'coin', '대란':'hot'}
    subjects = ['부동산', '경제', '주식', '찌라시', '가상화폐', '트윗', '대란']
    sites = ['클리앙', '딴지일보', '루리웹', '엠팍', '오유', '이토렌트', \
    '뽐뿌', 'SLR', '82cook', '인벤', 'DVD프라임']
    
    # Check Status file
    with open('./status.conf', 'r') as f:
        opt = json.load(f)

    if opt['status'] == 1:
        print('Running!')
    else:
        complete_subj_idx = subjects.index(opt['subject'])
        if complete_subj_idx == len(subjects)-1:
            subject_key = subjects[0]
        else:
            subject_key = subjects[complete_subj_idx+1]
        #print(subject_key)
        # 실행중 상태 기록
        opt['status'] = 1
        opt['subject'] = subject_key
        with open('./status.conf', 'w') as f:
            json.dump(opt, f)

        # log 메세지 생성
        log = '[ %s ]\n' % subject_key
        # 코드 동작 시간 측정용
        start_time = datetime.now().replace(microsecond=0)
        # 로깅
        log += 'Start_time: ' + str(start_time) + '\n'
        print(log)

        #subject = [subject] # character를 interate하지 않도록
        # 검색 url 불러오기
        with open('./links/' + subject[subject_key] + '.json','r') as f:
            url = json.load(f)
        for i, site in enumerate(sites):
            try:
                print(subject_key + ' | ' + site)
                ## article 가져오기
                result = F_common.scrapper(site, url)
                print(result.shape)
                if result.shape[0] >= 1:
                    ### 단어 필터링
                    result = F_common.word_filter(result, subject_key)
                    ### 주제 적합성 판정(트윗 제외)
                    if subject_key not in ['트윗', '대란']:
                        result = F_Classifier.predict_Y(result, subject[subject_key])
                    ### DB에 게시글 저장
                    article_count = F_common.store_db(subject[subject_key], site, result)
                else:
                    article_count = 0
                log += '-%s: %d개 수집\n' % (site, article_count)
            except Exception as e:
                print(e)
            ## 프린트 메시지
            print('%s - %s 완료' % (subject_key, site))
        # md 파일 생성
        if subject_key != '대란':
            execute_md(subject_key, size=300)
        end_time = datetime.now().replace(microsecond=0)
        # log에 동작 시간 추가
        message = '업데이트 동작 시간: %s\n' % str(end_time - start_time)
        log += message; print(message)

        # 게시물 수집 log 텔레그램으로 전송하기 위해 파일로 저장
        with open('./log/scrap.log', 'a') as f:
            f.write(log)
        ## 11개의 사이트가 전부 수집이 될 때만 전송
        if complete_subj_idx == len(subjects)-1:
            # 과거 log 불러오기
            with open('./log/scrap.log', 'r') as f:
                scrap_log = ''.join(f.readlines())
            # 텔레그램으로 발송
            TelegramBot().log_to_me(scrap_log)
            # 로그파일 초기화
            with open('./log/scrap.log', 'w') as f:
                f.write('')

        
        # 작업 종료 상태 기록
        opt['status'] = 0
        with open('./status.conf', 'w') as f:
            json.dump(opt, f)
