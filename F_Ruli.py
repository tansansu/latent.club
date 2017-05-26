# 2017.02.01

import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from lxml import html


# Modifing user_ids
def mod_user_id(char):
    result = char.replace(" ", '').replace('\r', '').replace('\n', '').replace('\t', '')
    return(result)


def mod_date(char):
    result = re.search(r'(\d{4}.{15})', char).group()
    result = result.replace(".", '-').replace('(', ' ')
    return(result)

re.compile('subject_link.*')
# 게시글 수집
def get_article(url):
    # Get a html
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    # Extracting articles from the html
    articles = soup.findAll('tr', {'class':'table_body'})[1:] # 맨 첫글 공지 제외
    # 유동적인 상단 공지글 제외(strong 태그) 
    articles = [a for a in articles \
    if str(a.find('a', {'class':re.compile(r'subject_link')})).__contains__('strong') == False]

    noti = articles[0].find('strong').text
    if noti == '결과없음':
        return(pd.DataFrame())

    # Extracting elements from articles
    a_list = []
    for a in articles:
        l = []
        title = a.findAll('a', {'class':'subject_link'})[0].text
        title
        user_id = mod_user_id(a.findAll('span', {'class':'writer'})[0].text)
        article_link = a.findAll('a', {'class':'subject_link'})[0].get('href')
        # print(article_link)
        article_id = re.search(r'(\d{8})', article_link).group()
        # Gathering the cotent of each article
        con = BeautifulSoup(urlopen(article_link), 'html.parser')
        date = mod_date(mod_user_id(con.find('span', {'class':'regdate'}).text))
        content = ''
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

