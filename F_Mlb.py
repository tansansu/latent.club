# 2017.02.04

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
    REFERER = 'http://mlbpark.donga.com/mlbpark/'

    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)


# 게시글 수집
def get_article(url):
    # Get a html
    s = sess()
    s_result = s.get(url)

    # Extracting articles from the html
    elem = html.fromstring(s_result.text)
    articles = elem.cssselect('tbody')[0].cssselect('tr')
    articles = articles[2:]
    if len(articles) == 0:
        return(pd.DataFrame())

    a_list = []
    for a in articles:
        l = []
        title = a.cssselect('td')[1].cssselect('a')[0].get('title').strip()
        user_id = a.cssselect('td')[2].cssselect('span')[1].text_content()
        # user_id = mod_user_id(user_id)
        article_link = a.cssselect('td')[1].cssselect('a')[0].get('href').strip()
        # print(article_link)
        article_id = re.search(r'(\d{18})', article_link).group()
        # Gathering the cotent of each article
        con = s.get(article_link)
        temp = html.fromstring(con.text)
        date = temp.cssselect('ul.view_head')[0].cssselect('span.val')[3].text_content()
        #date = mod_user_id(date)
        content = temp.cssselect('div.ar_txt')[0].text_content()

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
    print(result.describe())
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return(result)
