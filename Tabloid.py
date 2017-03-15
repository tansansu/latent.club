# 2017.03.07

import sqlite3
import pandas as pd
import sys
sys.path
sys.path.insert(0, 'latent_info/')
import F_common

subject = 'tabloid'

try:
    # 클리앙
    site = '클리앙'
    ## subject link
    clien_url = {'찌라시': \
        'http://m.clien.net/cs3/board?bo_table=park&bo_style=lists&sca=&sfl=wr_subject_content&stx=%EC%B0%8C%EB%9D%BC%EC%8B%9C'\
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
    ddan_url = {'찌라시':\
        'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword=%EC%B0%8C%EB%9D%BC%EC%8B%9C&m=1', \
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
    ruli_url = {'찌라시':\
        'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key=%EC%B0%8C%EB%9D%BC%EC%8B%9C', \
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
    mlb_url = {'찌라시':\
        'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query=%EC%B0%8C%EB%9D%BC%EC%8B%9C&x=0&y=0', \
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
    Eto_url = {'찌라시':\
        'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx=%C2%EE%B6%F3%BD%C3&x=0&y=0', \
        }
    ## Get articles
    result = F_common.scrapper(site, Eto_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass

try:
    # 웃긴대학
    site = '웃대'
    HuU_url = {'찌라시':\
        'http://m.humoruniv.com/board/list.html?table=pdswait&st=subject&searchday=1year&sk=%C2%EE%B6%F3%BD%C3', \
        }
    ## Get articles
    result = F_common.scrapper(site, HuU_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass


try:
    # 뽐뿌
    site = '뽐뿌'
    ppom_url = {'찌라시':\
        '%EC%B0%8C%EB%9D%BC%EC%8B%9C', \
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
    slr_url = {'찌라시':\
        '%EC%B0%8C%EB%9D%BC%EC%8B%9C', \
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
    cook82_url = {'찌라시':\
        '%EC%B0%8C%EB%9D%BC%EC%8B%9C', \
        }
    ## Get articles
    result = F_common.scrapper(site, cook82_url)
    ## DB에 게시글 저장
    F_common.store_db(subject, site, result)
except:
    pass


## Making MD files
### Getting a data from DB
with sqlite3.connect('db/board.db') as conn:
    query = 'select site, title, article_link, date_time from ' + subject + \
    ' order by date_time desc limit 400;'
    tabloid = pd.read_sql_query(query, conn)

### ordering by date/time
tabloid.sort_values('date_time', ascending=False, inplace=True)

### Splitting of the dataframe for 3 pages
tabloid_1 = tabloid.iloc[:60]
tabloid_2 = tabloid.iloc[60:120]
tabloid_3 = tabloid.iloc[120:]

### Making the markdown file
directory = '/Users/tansansu/Google Drive/blog/latent-info/content/' + subject
F_common.to_md(tabloid_1, '찌라시', directory, 1)
F_common.to_md(tabloid_2, '찌라시', directory, 2)
F_common.to_md(tabloid_3, '찌라시', directory, 3)

F_common.export_sample(tabloid, "tabloid")