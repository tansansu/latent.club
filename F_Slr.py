# 2017.04.30

import time
import requests
import urllib
import re
import pandas as pd
from datetime import datetime
from lxml import html
from bs4 import BeautifulSoup


# cleansing a article title
def mod_title(char):
    result = char.replace('\r', '').replace('\n', '').replace('\t', '')
    # Removing a number of replies
    result = re.sub(r"\[[0-9]+\]", '', result)
    return(result)


# Session
def sess(url):
    AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
    REFERER = url

    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)


# 게시글 수집
def get_article(url):
    base_url = 'http://starboard.kr/slr'
    search_url = 'http://starboard.kr/conn/board/search'
    # Get a html
    s = sess('http://starboard.kr/')
    base = s.get(base_url)
    # s_result.encoding = 'euc-kr' # Revising the encoding
    # Extracting articles from the html
    payload = {'search_text':url}
    s_result = s.post(search_url, data=payload)

    soup = BeautifulSoup(s_result.text, 'html.parser')
    articles = soup.findAll('div', attrs={'class':'ItemContent Discussion'})
    # print(articles)
    a_list = []
    for a in articles:
        l = []
        title = mod_title(a.find('div', attrs={'class':'Title'}).find('a').text)
        try:
            article_link = a.find('div', attrs={'class':'Title'}).find('a')['href']
        except:
            continue
        # print(article_link)
        article_id = re.search(r'(\d{8})', article_link).group()
        date = a.find('time')['datetime']
        # Get a content of the article
        s = sess('http://www.slrclub.com/')
        con = BeautifulSoup(s.get(article_link).text, 'html.parser')
        member_id = con.find('span', attrs={'class':'lop'})
        # 존재하지 않는 게시물 예외 처리
        if member_id is None:
            member_id = ''
        else:
            member_id = con.find('span', attrs={'class':'lop'}).text
        content = con.find('div', attrs={'id':'userct'})
        if content is None:
            content = ''
        else:
            content = con.find('div', attrs={'id':'userct'}).text


        # Making the list
        l.append(title)
        l.append(date)
        l.append(article_id)
        l.append(member_id)
        l.append(article_link)
        l.append(content)
        a_list.append(l)
        time.sleep(.5)

    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result = result[result['member_id'] != '']
    result.set_index('article_id')

    return(result)
