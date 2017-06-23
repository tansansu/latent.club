# 2017.06.20

import time
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime


# 함수: 세션생성
def sess():
    AGENT = 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    REFERER = 'http://www.ddanzi.com/'

    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)

def mod_reply(char):
    try:
        return(re.search(r'[0-9]+', char.find('span', {'class':'reply'}).text).group())
    except:
        return('0')

# 함수: 게시글 수집
def get_article(url):
    # 사이트에서 html 가져오기
    s = sess()
    s_result = s.get(url)
    soup = BeautifulSoup(s_result.text, 'html.parser')
    articles = soup.findAll('li')
    # 게시글만 추출
    articles = [a for a in articles if a.find('dd') is not None]
    a = articles[1]
    # 게시글이 없는 경우 빈 데이터 프레임 리턴
    if len(articles) == 0:
        return(pd.DataFrame())

    # 추출 요소
    a_list = []
    for a in articles:
        l = []
        a.find('')
        title = a.find('dt').find('a').text
        user_id = a.find('strong').text
        article_link = a.find('a')['href']
        # print(article_link)
        article_id = re.search(r'(\d{9})', article_link).group()
        date = a.find('span', {'class':'time'}).text
        reply_num = mod_reply(a)
        view_num = a.find('span', {'class':'readNum'}).text
        content = ''
        # 추출항목 리스트로 생성
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

    # 결과 데이터 프레임 생성
    result = pd.DataFrame(a_list)
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    ## Excepting the particular articles by '펌쟁이'
    result = result[result['member_id'] != '펌쟁이']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return(result)
