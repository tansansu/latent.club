# 2017.03.15

import json
import sqlite3
import pandas as pd
import sys
sys.path
sys.path.insert(0, 'latent_info/')
import F_common

subject = 'economy'

site_link = {'클리앙':'clien', '딴지일보':'ddan', \
    '루리웹':'ruli', '엠팍':'mlb', '웃대':'HuU', '이토렌트':'eto', '뽐뿌':'ppom', \
    'SLR':'slr', '82cook':'82cook'}

with open('links/' + subject + '.json','r') as f:
        url = json.load(f)

for s in site_link:
    try:
        ## article 가져오기
        result = F_common.scrapper(s, url[site_link[s]])
        ## DB에 게시글 저장
        F_common.store_db(subject, s, result)
    except:
        pass

## Making MD files
### Getting a data from DB
with sqlite3.connect('db/board.db') as conn:
    query = 'select site, title, article_link, date_time from ' + subject + \
    ' order by date_time desc limit 400;'
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

