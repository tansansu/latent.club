# 2017.12.31

import time
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime


# 함수: 세션생성
def sess():
    AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
    REFERER = 'http://www.ddanzi.com/'

    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)

def mod_char(char):
    return(char.replace('\n', '').replace('\t', ''))

def mod_reply(char):
    try:
        return(char.replace('[', '').replace(']', ''))
    except:
        return('0')


# 함수: 게시글 수집
def get_article(url):
    # 사이트에서 html 가져오기
    s = sess()
    s_result = s.get(url)
    soup = BeautifulSoup(s_result.text, 'html.parser')
    articles = soup.findAll('li', {'class':'notice'})
    # 게시글만 추출
    articles = [x for x in articles if x.find('span', {'class':'author'}).text != '죽지않는돌고래']
    # 게시글이 없는 경우 빈 데이터 프레임 리턴
    if len(articles) == 0:
        return(pd.DataFrame())

    # 추출 요소
    a_list = []
    for a in articles:
        l = []

        title = mod_char(a.find('span', {'class':'title'}).text)
        user_id = a.find('span', {'class':'author'}).text
        article_link = a.find('a', {'class':'link'})['href']
        # print(article_link)
        article_id = re.search(r'(\d{9})', article_link).group()
        reply_num = mod_reply( a.find('span', {'class':'talk'}).text)
        view_num = a.find('span', {'class':'hits'}).text.replace('|', '')
        # 날짜를 구하기 위해 게시글 클릭
        cont = BeautifulSoup(s.get(article_link).text, 'html.parser')
        date = cont.find('p', {'class':'time'}).text.replace('|', '')
        if len(date) < 9:
            date = str(datetime.now()).split(' ')[0] + ' ' + date
        else:
            date = date.replace('.', '-')

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
        time.sleep(1.3)

    # 결과 데이터 프레임 생성
    result = pd.DataFrame(a_list)
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    ## Excepting the particular articles by '펌쟁이'
    result = result[result['member_id'] != '펌쟁이']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return(result)
