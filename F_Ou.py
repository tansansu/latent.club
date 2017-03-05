# 2017.02.07

import time
import requests
import urllib
import re
import pandas as pd
from datetime import datetime
from lxml import html

# Session
def sess():
    AGENT = 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    REFERER = 'http://m.todayhumor.co.kr/'
    
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)

url = 'http://m.todayhumor.co.kr/list.php?kind=search&table=total&search_table_name=total&keyfield=subject&keyword=%EB%B6%80%EB%8F%99%EC%82%B0'

# 게시글 수집
def get_article(url):
    # Get a html
    s = sess()
    s_result = s.get(url)
    s_result.encoding = 'euc-kr' # Revising the encoding
    # Extracting articles from the html
    elem = html.fromstring(s_result.text)
    articles = elem.cssselect('div.bbs')
    if len(articles) == 0:
        return(pd.DataFrame())
        
    a_list = []
    for a in articles:
        l = []
        title = a.cssselect('dl')[0].cssselect('dt')[0].cssselect('a')[0].text_content()
        user_id = a.cssselect('address')[0].cssselect('strong')[0].text_content()
        article_link = a.cssselect('a')[0].get('href').strip()
        print(article_link)
        article_id = re.search(r'(\d{9})', article_link).group()
        date = a.cssselect('address')[0].cssselect('span')[0].text_content()
        # Gathering the cotent of each article
        con = s.get(article_link)
        temp = html.fromstring(con.text)
        try:
            content = temp.cssselect('div.content')[0].cssselect('div.bd')[0].\
            cssselect('div.co')[0].text_content()
        except:
            content = a.cssselect('dl')[0].cssselect('dd')[0].text_content()
        # Making the list
        l.append(title)
        l.append(date)
        l.append(article_id)
        l.append(user_id)
        l.append(article_link)
        l.append(content)
        a_list.append(l)
        time.sleep(.5)
        
    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')
    
    return(result)

