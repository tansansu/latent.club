# 2017.03.07
# 부동산 글 수집

import sqlite3
import pandas as pd
import time
import sys
sys.path
sys.path.insert(0, 'latent_info/')
import F_common
import F_Classifier

subject = 'estate'

try:
    # 클리앙
    site = '클리앙'
    ## subject link
    clien_url = {'부동산':\
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EB%B6%80%EB%8F%99%EC%82%B0', \
        '전월세':\
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EC%A0%84%EC%9B%94%EC%84%B8', \
        '재건축':\
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EC%9E%AC%EA%B1%B4%EC%B6%95', \
        '집값':\
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EC%A7%91%EA%B0%92'\
        }
    ## Get articles
    result = F_common.scrapper(site, clien_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass

try:
    # 딴지일보
    site = '딴지일보'
    ddan_url = {'부동산':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&is_keyword=%EB%B6%80%EB%8F%99%EC%82%B0&m=1', \
        '전월세':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword=%EC%A0%84%EC%9B%94%EC%84%B8&m=1', \
        '재건축':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword=%EC%9E%AC%EA%B1%B4%EC%B6%95', \
        '집값':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword=%EC%A7%91%EA%B0%92&m=1'\
        }
    ## Get articles
    result = F_common.scrapper(site, ddan_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass

try:
    # 루리웹
    site = '루리웹'
    ruli_url = {'부동산':\
        'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key=%EB%B6%80%EB%8F%99%EC%82%B0', \
        '집값':\
        'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key=%EC%A7%91%EA%B0%92'\
        }
    ## Get articles
    result = F_common.scrapper(site, ruli_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass

try:
    # 엠엘비파크
    site = '엠팍'
    mlb_url = {'부동산':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EB%B6%80%EB%8F%99%EC%82%B0&x=0&y=0', \
        '전월세':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EC%A0%84%EC%9B%94%EC%84%B8&x=0&y=0', \
        '재건축':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EC%9E%AC%EA%B1%B4%EC%B6%95&x=0&y=0', \
        '집값':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EC%A7%91%EA%B0%92&x=0&y=0'\
        }
    ## Get articles
    result = F_common.scrapper(site, mlb_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass

try:
    # 웃긴대학
    site = '웃대'
    HuU_url = {'부동산':\
        'http://m.humoruniv.com/board/list.html?table=pdswait&st=subject&searchday=1year&sk=%BA%CE%B5%BF%BB%EA', \
        '집값':\
        'http://m.humoruniv.com/board/list.html?table=pdswait&st=subject&searchday=1year&sk=%C1%FD%B0%AA'\
        }
    ## Get articles
    result = F_common.scrapper(site, HuU_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass

try:
    # 이토렌트
    site = '이토렌트'
    Eto_url = {'부동산':\
        'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx=%BA%CE%B5%BF%BB%EA&x=20&y=7', \
        '전월세':\
        'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx=%C0%FC%BF%F9%BC%BC&x=25&y=9', \
        '재건축':\
        'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject&stx=%C0%E7%B0%C7%C3%E0&x=0&y=0', \
        '집값':\
        'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx=%C1%FD%B0%AA&x=0&y=0'\
        }
    ## Get articles
    result = F_common.scrapper(site, Eto_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass


try:
    # 뽐뿌
    site = '뽐뿌'
    ppom_url = {'부동산':\
        '%EB%B6%80%EB%8F%99%EC%82%B0', \
        '전월세':\
        '%EC%A0%84%EC%9B%94%EC%84%B8', \
        '재건축':\
        '%EC%9E%AC%EA%B1%B4%EC%B6%95', \
        '집값':\
        '%EC%A7%91%EA%B0%92'\
        }
    ## Get articles
    result = F_common.scrapper(site, ppom_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass


try:
    # SLR
    site = 'SLR'
    slr_url = {'부동산':\
        '%EB%B6%80%EB%8F%99%EC%82%B0', \
        '전월세':\
        '%EC%A0%84%EC%9B%94%EC%84%B8', \
        '재건축':\
        '%EC%9E%AC%EA%B1%B4%EC%B6%95', \
        '집값':\
        '%EC%A7%91%EA%B0%92'\
        }
    ## Get articles
    result = F_common.scrapper(site, slr_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass


try:
    # 82쿡
    site = '82cook'
    cook82_url = {'부동산':\
        '%EB%B6%80%EB%8F%99%EC%82%B0', \
        '전월세':\
        '%EC%A0%84%EC%9B%94%EC%84%B8', \
        '재건축':\
        '%EC%9E%AC%EA%B1%B4%EC%B6%95', \
        '집값':\
        '%EC%A7%91%EA%B0%92'\
        }
    ## Get articles
    result = F_common.scrapper(site, cook82_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass



## md파일 생성
### db파일에서 게시글 리스트 추출
dir_db = '/Users/tansansu/Google Drive/Python/latent_info/board.db'
with sqlite3.connect(dir_db) as conn:
    query = 'select site, title, article_link, date_time from ' + subject + \
    ' order by date_time desc limit 300;'
    estate = pd.read_sql_query(query, conn)
### 날짜/시간 역순으로 ordering
estate.sort_values('date_time', ascending=False, inplace=True)

### 머신러닝 분류
estate = F_Classifier.predict_Y(estate)
estate = estate[estate['result'] == 'Y']

### 데이터 프레임을 3개 페이지로 나누기
estate_1 = estate.iloc[:60]
estate_2 = estate.iloc[60:120]
estate_3 = estate.iloc[120:180]

### 각각의 데이터프레임을 3개의 md파일(페이지)로 만들기
directory = '/Users/tansansu/Google Drive/blog/latent-info/content/' + subject
F_common.to_md(estate_1, '부동산', directory, 1)
F_common.to_md(estate_2, '부동산', directory, 2)
F_common.to_md(estate_3, '부동산', directory, 3)

