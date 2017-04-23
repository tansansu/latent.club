# 2017.03.20

import time
import requests
import urllib
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from lxml import html


# 게시글 수집
def get_article(url):
    base_url = 'http://m.humoruniv.com/board/'
    # Get a html
    s_result = requests.get(url)
    s_result.encoding = 'euc-kr' # Revising the encoding
    # Extracting articles from the html
    elem = html.fromstring(s_result.text)
    soup = BeautifulSoup(s_result.text, 'html.parser')

    title = soup.find_all('span', {'class':'link_hover'})
    if len(soup) == 0:
        return(pd.DataFrame())
    user_id = soup.find_all('span', {'class':'hu_nick_txt'})
    link_temp = soup.find_all('a', {'class':'list_body_href'})
    article_link = []
    for a in link_temp:
        article_link.append(base_url + a['href'])
    article_id = []
    for a in article_link:
        article_id.append( re.search(r'(\d{7})', a).group())
    
    a_list = []
    for i in range(len(title)):
        l = []
        l.append(title[i].text)
        ## 날짜와 시간 가져오기
        con = requests.get(article_link[i])
        con.encoding = 'euc-kr'
        temp = html.fromstring(con.text)
        try:
            # content = ''
            date = temp.cssselect('span.etc')[0].text_content()
        except:
            continue
        # Making the list
        l.append(date)
        l.append(article_id[i])
        l.append(user_id[i].text)
        l.append(article_link[i])
        l.append('') # content 미수집
        time.sleep(.5)
        a_list.append(l)

    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content']
    result['date_time'] = pd.to_datetime(result['date_time'])

    return(result)

