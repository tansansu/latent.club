# 2018.01.01

import json
import pandas as pd
import os
import time
from multiprocessing import Pool
import pickle
import sqlite3
from sh import git, cd
import sys
sys.path.insert(0, 'latent_info/')
sys.path.append('/home/revlon/Codes/Telegram_Bot/')
sys.path.append('/Users/tansansu/Google Drive/Python/Telegram_Bot/')
sys.path.append('/root/Codes/Telegram_Bot/')
import F_common
from TelegramBot import TelegramBot


class Updater:
    def __init__(self):
        # 기준 정보
        self.subject_dict = {'부동산': 'estate', '찌라시': 'tabloid', '주식': 'stock',
                             '경제': 'economy', '트윗': 'tweet', '가상화폐': 'coin',
                             '대란': 'hot', '감동': 'touching', '근황': 'tidings'}
        self.subjects = ['부동산', '경제', '주식', '찌라시', '가상화폐', '트윗', '대란', '감동', '근황']
        self.subject = ''
        self.site_dict = {'클리앙': 'clien', '딴지일보': 'ddan', '루리웹': 'ruli',
            '엠팍': 'mlb', '오유': 'Ou', '이토렌트': 'eto', '뽐뿌': 'ppom',
            'SLR': 'slr', '82cook': '82cook', '인벤': 'inven', 'DVD프라임': 'dvd'}
        self.site_dict_rev = dict(zip(self.site_dict.values(), self.site_dict.keys()))
        self.sites = ['클리앙', '딴지일보', '루리웹', '엠팍', '오유', '이토렌트',
            '뽐뿌', 'SLR', '82cook', '인벤', 'DVD프라임']
        self.classifier = None
        self.log = ''  # 로깅용 스트링
        self.start_time = 0
        self.end_time = 0

    # 함수: 게시판 md 파일 생성 작업 실행
    def execute_md(self, size):
        # db파일에서 게시글 리스트 추출
        if self.subject == 'stock':  # 주식 게시판에서 코인 글은 제외
            query = 'select site, title, article_link, date_time, view_num, reply_num from \
            (select site, title, article_link, date_time, view_num, reply_num, article_id from \
            %s where result = "Y" order by date_time desc limit %d) where article_id not in \
            (select article_id from coin order by date_time desc limit %d) limit %d;' % \
                (self.subject_dict[self.subject], size, size, size)
        else:
            query = 'select site, title, article_link, date_time, view_num, reply_num from \
            %s where result = "Y" order by date_time desc limit %d;' % (self.subject_dict[self.subject], size)
        conn = sqlite3.connect('./db/board.db')
        df = pd.read_sql(query, conn)
        conn.close()
        # 중복글 제거(제목)
        df.drop_duplicates('title', inplace=True)
        # 데이터 프레임을 5개 페이지로 나누어서 md파일(페이지)로 만들기
        #directory = '/Users/tansansu/Google Drive/Python/latent_info/latent-info/content/' + self.subject_dict[self.subject]
        directory = '/home/revlon/Codes/Web/hugo_latent-info/content/' + self.subject_dict[self.subject]
        for i in range(7):
            F_common.to_md(df.iloc[30*i:30*(i+1)], self.subject, directory, i+1)

    # 텔레그램 메세지 보내는 함수
    @staticmethod
    def log2telegram(message):
        TelegramBot().latent_noti(message)

    # 멀티프로세싱으로 스크래핑 처리
    def multi_operation(self, input_sites):
        pool = Pool(3)
        pool.map(self.run, input_sites)

    # 업데이트 실행 함수
    def run(self, site):
        # 검색 url 불러오기
        with open('links/' + self.subject_dict[self.subject] + '.json', 'r') as f:
            url = json.load(f)
        try:
            print(self.subject + ' | ' + site)
            # article 가져오기
            result = F_common.scrapper(site, url, self.subject_dict[self.subject], self.site_dict)
            print("%s - scraped articles: %d - %d" % (site, result.shape[0], result.shape[1]))
            if result.shape[0] > 0:
                # 단어 필터링
                result = F_common.word_filter(result, self.subject)
                print("%s - filtered aritcles: %d - %d" % (site, result.shape[0], result.shape[1]))
            if result.shape[0] > 0:
                # 수집한 게시물이 db에 이미 있는 것인지 비교
                result = F_common.compare_article(self.subject_dict[self.subject], site, result)
                print("%s - no duplication articles: %d - %d" % (site, result.shape[0], result.shape[1]))
            if result.shape[0] > 0:
                file_path = 'temp/%s.pkl' % self.site_dict[site]
                #print("create temp file: " + file_path)
                with open(file_path, 'wb') as f:
                    pickle.dump(result, f)
        except Exception as e:
            print("run error", e.args)
        # 임시파일로 저장
        print('%s - %s 수집 완료' % (self.subject, site))

    # 주제 적합성 판정(트윗, 감동 제외) 후 DB 저장
    def predict_store(self, df):
        if self.subject == "찌라시":
            result = self.classifier.predict_ddan(df)
        elif self.subject not in ['트윗', '감동', '근황']:
            result = self.classifier.predict_Y(df)
        else:
            result = df
        # DB에 게시글 저장
        article_count = F_common.store_db(self.subject_dict[self.subject], result)
        print("stored aritcles: %d" % result.shape[0])
        return article_count

    # hugo static page 생성
    @staticmethod
    def run_hugo(path):
        os.system('cd %s && hugo --theme=hugo-material-docs' % path)

    # Git commit 실행
    @staticmethod
    def git_commit(path):
        cd(path)
        git.add('--all')
        print('git add --all')
        time.sleep(8)
        git.commit(m='regular uploading of articles')
        print('git commit -m message')
        time.sleep(8)
        git.push('origin', 'master')
        print('git push origin master')
