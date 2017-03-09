# 2017.03.08

import sqlite3
import pandas as pd
import sys
sys.path
sys.path.insert(0, 'latent_info/')
import F_common

subject = 'stock'

try:
    # 클리앙
    site = '클리앙'
    ## subject link
    clien_url = {'주식': \
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EC%A3%BC%EC%8B%9D',\
        '거래량':\
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EA%B1%B0%EB%9E%98%EB%9F%89',\
        '단타':\
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EB%8B%A8%ED%83%80'\
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
    ddan_url = {'주식':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword=%EC%A3%BC%EC%8B%9D&m=1', \
        '거래량':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword=%EA%B1%B0%EB%9E%98%EB%9F%89&m=1',\
        '단타':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword=%EB%8B%A8%ED%83%80&m=1'\
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
    ruli_url = {'주식':\
        'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key=%EC%A3%BC%EC%8B%9D', \
        '단타':\
        'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key=%EB%8B%A8%ED%83%80'\
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
    mlb_url = {'주식':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EC%A3%BC%EC%8B%9D&x=0&y=0', \
        '거래량':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EA%B1%B0%EB%9E%98%EB%9F%89&x=0&y=0',\
        '단타':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EB%8B%A8%ED%83%80&x=0&y=0'\
    }
    ## Get articles
    result = F_common.scrapper(site, mlb_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass

try:
    # 이토렌트
    site = '이토렌트'
    Eto_url = {'주식':\
        'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx=%C1%D6%BD%C4&x=10&y=16'\
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
    ppom_url = {'주식':\
        '%EC%A3%BC%EC%8B%9D'\
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
    slr_url = {'주식':\
        '%EC%A3%BC%EC%8B%9D'\
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
    cook82_url = {'주식':\
        '%EC%A3%BC%EC%8B%9D'\
        }
    ## Get articles
    result = F_common.scrapper(site, cook82_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass


## Making MD files
### Getting a data from DB
dir_db = '/Users/tansansu/Google Drive/Python/latent_info/board.db'
with sqlite3.connect(dir_db) as conn:
    query = 'select site, title, article_link, date_time from ' + subject + \
    ' order by date_time desc limit 180;'
    stock = pd.read_sql_query(query, conn)

### ordering by date/time
stock.sort_values('date_time', ascending=False, inplace=True)

### Splitting of the dataframe for 3 pages
stock_1 = stock.iloc[:60]
stock_2 = stock.iloc[60:120]
stock_3 = stock.iloc[120:]

### Making the markdown file
directory = '/Users/tansansu/Google Drive/blog/latent-info/content/' + subject
F_common.to_md(stock_1, '주식', directory, 1)
F_common.to_md(stock_2, '주식', directory, 2)
F_common.to_md(stock_3, '주식', directory, 3)
