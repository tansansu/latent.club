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
    REFERER = 'http://www.todayhumor.co.kr/'
    
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)


# 게시글 수집
def get_article(url):
    base_url = 'http://m.humoruniv.com/board/'
    # Get a html
    s = sess()
    s_result = s.get(url)
    s_result.encoding = 'euc-kr' # Revising the encoding
    # Extracting articles from the html
    elem = html.fromstring(s_result.text)
    articles = elem.cssselect('ul')[0]
    if len(articles) == 0:
        return(pd.DataFrame())
    a_list = []
    for a in articles:
        l = []
        title = a.cssselect('span.link_hover')[0].text_content()
        user_id = a.cssselect('span.hu_nick_txt')[0].text_content()
        article_link = base_url + a.get('href')
        article_id = re.search(r'(\d{7})', article_link).group()
        # Gathering the cotent of each article
        con = s.get(article_link)
        con.encoding = 'euc-kr'
        temp = html.fromstring(con.text)
        try:
            content = temp.cssselect('div.wrap_body')[0].text_content()
            date = temp.cssselect('span.etc')[0].text_content()
        except:
            continue
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

