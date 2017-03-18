# 2017.02.01

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
    REFERER = 'http://m.ruliweb.com'

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
    articles = elem.cssselect('tr.table_body')
    articles = articles[2:]
    if len(articles) == 0:
        return(pd.DataFrame())
        
    a_list = []
    for a in articles:
        l = []
        title = a.cssselect('td.subject')[0].cssselect('div')[0].cssselect('a')[1].text_content()
        user_id = a.cssselect('td.subject')[0].cssselect('div')[1].cssselect('span')[0].text_content()
        user_id = mod_user_id(user_id)
        article_link = a.cssselect('td.subject')[0].cssselect('div')[0].cssselect('a')[1].get('href').strip()
        # print(article_link)
        article_id = re.search(r'(\d{8})', article_link).group()
        # Gathering the cotent of each article
        con = s.get(article_link)
        temp = html.fromstring(con.text)
        date = temp.cssselect('div.info_wrapper')[0].cssselect('span')[4].\
        cssselect('span')[0].text_content()
        date = mod_user_id(date)
        date = mod_date(date)
        content = temp.cssselect('div.board_main_view')[0].cssselect('div.view_content')[0].\
        cssselect('div.row')[0].text_content()

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


# Modifing user_ids
def mod_user_id(char):
    result = char.replace(" ", '').replace('\r', '').replace('\n', '').replace('\t', '')
    return(result)


def mod_date(char):
    result = re.search(r'(\d{4}.{15})', char).group()
    result = result.replace(".", '-').replace('(', ' ')
    return(result)
