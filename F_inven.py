# 2017.06.06

import time
from urllib.request import urlopen
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

# 아이디 글자의 Level 표시 삭제
def mod_id(char):
    result = re.sub(r'L.*', '', char)
    return(result.replace(' ', ''))

def mod_reply(char):
    try:
        return(char.find('a', {'class':re.compile(r'^cmt')}).text)
    except:
        return('0')

# 게시글 수집
def get_article(url):
    base_url = 'http://m.inven.co.kr'
    # Get a html
    resp = urlopen(url)
    soup = BeautifulSoup(resp, 'html.parser')
    articles = soup.findAll('li', {'class':'articleSubject'})
    # 배너 광고 삭제
    articles = [x for x in articles if x.find('em') is not None]
    # Return empty dataframe if no articles
    if len(articles) == 0:
        return(pd.DataFrame())
    # 검색 글 없을 때 출력되는 메세지가 나타나면 리턴
    elif articles[0].find('span', {'class':'title'}).text.__contains__('검색된'):
        return(pd.DataFrame())
    
    a_list = []
    for a in articles:
        l = []
        article_link = base_url + a.find('a', {'class':'subject'})['href']
        title = a.find('span', {'class':'title'}).text
        user_id = a.find('em', {'class':'writer'}).text
        user_id = mod_id(user_id)
        article_id = re.search(r'(\d{6,})', article_link).group()
        # scrapping a date, a time and a content
        date = a.find('span', {'class':'postdate'}).find('span')['title']
        content = ''
        reply_num = mod_reply(a)
        view_num = re.search(r'[0-9]+', a.find('span', {'class':'hit'}).text).group()
        # Making the list
        l.append(title)
        l.append(date)
        l.append(article_id)
        l.append(user_id)
        l.append(article_link)
        l.append(content)
        l.append(reply_num)
        l.append(view_num)
        a_list.append(l)
        time.sleep(.5)

    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return(result)
