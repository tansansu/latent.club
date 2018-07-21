# 2018.01.01

import json
import sqlite3
import pandas as pd
import sys
sys.path.insert(0, 'latent_info/')
sys.path.append('/home/revlon/Codes/Telegram_Bot/')
sys.path.append('/Users/tansansu/Google Drive/Python/Telegram_Bot/')
#sys.path.append('/home/jar/Codes/Telegram_Bot/')
import F_common 
import F_Classifier
from datetime import datetime
from TelegramBot import TelegramBot



class Updater:
    def __init__(self):
        # 기준 정보
        self.subject_dict = {'부동산':'estate', '찌라시':'tabloid', '주식':'stock', \
        '경제':'economy', '트윗':'tweet', '가상화폐':'coin', '대란':'hot', '감동':'touching'}
        self.subjects = ['부동산', '경제', '주식', '찌라시', '가상화폐', '트윗', '대란', '감동']
        self.sites = ['클리앙', '딴지일보', '루리웹', '엠팍', '오유', '이토렌트', \
        '뽐뿌', 'SLR', '82cook', '인벤', 'DVD프라임']


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
    

    # 텔레그램 메세지 보내는 함수
    @staticmethod
    def log2telegram(message):
        TelegramBot().log_to_me(message)

    # 업데이트 실행 함수
    def run(self):
        # 코드 동작 시간 측정용
        start_time = datetime.now().replace(microsecond=0)
        log = 'Start_time: ' + str(datetime.now().replace(microsecond=0)) + '\n'
        print(log)

        # 전체 사이트 실행
        for subject in self.subjects:
            # log 메세지 생성
            log += '[ %s ]\n' % subject
            # 검색 url 불러오기
            with open('links/' + self.subject_dict[subject] + '.json','r') as f:
                url = json.load(f)
            
            # 사이트별로 게시글 스크래핑 
            for i, site in enumerate(self.sites):
                try:
                    print(subject + ' | ' + site)
                    ## article 가져오기
                    result = F_common.scrapper(site, url, self.subject_dict[subject])
                    print(result.shape)
                    if result.shape[0] >= 1:
                        ### 단어 필터링
                        result = F_common.word_filter(result, subject)
                        ### 주제 적합성 판정(트윗 제외)
                        if subject not in ['트윗', '대란', '감동']:
                            result = F_Classifier.predict_Y(result, self.subject_dict[subject])
                        ### DB에 게시글 저장
                        article_count = F_common.store_db(self.subject_dict[subject], site, result)
                    else:
                        article_count = 0
                    log += '-%s: %d개 수집\n' % (site, article_count)
                except Exception as e:
                    print(e)
                ## 프린트 메시지
                print('%s - %s 완료' % (subject, site))
            # md 파일 생성
            if subject not in ['대란', '감동']:
                self.execute_md(subject, size=300)
            
        end_time = datetime.now().replace(microsecond=0)
        # log에 동작 시간 추가
        message = '업데이트 동작 시간: ' + str(end_time - start_time)
        log += message; print(message)

