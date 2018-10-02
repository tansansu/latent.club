# 2018.01.01

import json
import sqlite3
import pandas as pd
import sys
sys.path.insert(0, 'latent_info/')
sys.path.append('/home/revlon/Codes/Telegram_Bot/')
sys.path.append('/Users/tansansu/Google Drive/Python/Telegram_Bot/')
sys.path.append('/root/Codes/Telegram_Bot/')
import F_common 
import F_Classifier
from TelegramBot import TelegramBot


class Updater:
    def __init__(self):
        # 기준 정보
        self.subject_dict = {'부동산': 'estate', '찌라시': 'tabloid', '주식': 'stock',
            '경제': 'economy', '트윗': 'tweet', '가상화폐': 'coin', '대란': 'hot', '감동': 'touching'}
        self.subjects = ['부동산', '경제', '주식', '찌라시', '가상화폐', '트윗', '대란', '감동']
        self.subject = ''
        self.sites = ['클리앙', '딴지일보', '루리웹', '엠팍', '오유', '이토렌트',
            '뽐뿌', 'SLR', '82cook', '인벤', 'DVD프라임']
        self.log = ''  # 로깅용 스트링
        self.start_time = 0
        self.end_time = 0

    # 함수: 게시판 md 파일 생성 작업 실행
    def execute_md(self, size):
        # db파일에서 게시글 리스트 추출
        conn = sqlite3.connect('db/board.db')
        if self.subject == 'stock':  # 주식 게시판에서 코인 글은 제외
            query = 'select site, title, article_link, date_time, view_num, reply_num from \
            (select site, title, article_link, date_time, view_num, reply_num, article_id from \
            %s where result = "Y" order by date_time desc limit %d) where article_id not in \
            (select article_id from coin order by date_time desc limit %d) limit %d;' % \
                (self.subject_dict[self.subject], size, size, size)
        else:
            query = 'select site, title, article_link, date_time, view_num, reply_num from \
            %s where result = "Y" order by date_time desc limit %d;' % (self.subject_dict[self.subject], size)
        df = pd.read_sql(query, conn)
        conn.close()
        # 중복글 제거(제목)
        df.drop_duplicates('title', inplace=True)
        # 데이터 프레임을 5개 페이지로 나누어서 md파일(페이지)로 만들기
        # directory = '/Users/tansansu/Google Drive/Python/latent_info/latent-info/content/' + self.subject_dict[self.subject]
        directory = '/home/revlon/Codes/Web/hugo_latent-info/content/' + self.subject_dict[self.subject]
        for i in range(7):
            F_common.to_md(df.iloc[30*i:30*(i+1)], self.subject, directory, i+1)

    # 텔레그램 메세지 보내는 함수
    @staticmethod
    def log2telegram(message):
        TelegramBot().log_to_me(message)

    # 업데이트 실행 함수
    def run(self, site):
        # 검색 url 불러오기
        with open('links/' + self.subject_dict[self.subject] + '.json', 'r') as f:
            url = json.load(f)
        try:
            print(self.subject + ' | ' + site)
            # article 가져오기
            result = F_common.scrapper(site, url, self.subject_dict[self.subject])
            if result.shape[0] >= 1:
                # 단어 필터링
                result = F_common.word_filter(result, self.subject)
                # 주제 적합성 판정(트윗 제외)
                if self.subject not in ['트윗', '감동']:
                    result = F_Classifier.predict_Y(result, self.subject_dict[self.subject])
                # DB에 게시글 저장
                article_count = F_common.store_db(self.subject_dict[self.subject], site, result)
            else:
                article_count = 0
        except Exception as e:
            print(e)
            article_count = 0
        # 프린트 메시지
        print('%s - %s 완료' % (self.subject, site))
        tmp_log = '-%s: %d개 수집\n' % (site, article_count)
        print(tmp_log)
        # md 파일 생성
        # if subject not in ['대란', '감동']:
        self.execute_md(size=300)

        # 게시물 수집 log 텔레그램으로 전송하기 위해 파일로 저장
        with open('./log/scrap.log', 'a') as f:
            f.write(tmp_log)

