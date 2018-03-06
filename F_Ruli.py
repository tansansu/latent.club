# 2017.06.14

import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime


# Modifing user_ids
def mod_user_id(char):
    result = char.replace(" ", '').replace('\r', '').replace('\n', '').replace('\t', '')
    return(result)

# 날짜 string 수정 함수
def mod_date(char):
    result = re.search(r'(\d{4}.{15})', char).group()
    result = result.replace(".", '-').replace('(', ' ')
    return(result)

# 리플수 string 수정 함수
def mod_reply(char):
    try:
        return(char.find('span', {'class':'num'}).text)
    except:
        return('0')


# 게시글 수집
def get_article(url):
    base_url = 'http://m.ruliweb.com/community/board/300148/read/'
    # Get a html
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    # Extracting articles from the html
    articles = soup.findAll('tr', {'class':'table_body'})[1:] # 맨 첫글 공지 제외
    # 유동적인 상단 공지글 제외(notice class 제거)
    articles = [a for a in articles if 'notice' not in a.get('class')]
    # 유동적인 결과없음 글이 있으면 리턴
    if articles[0].find('strong').text == '결과없음':
        return(pd.DataFrame())

    # Extracting elements from articles
    a_list = []
    for a in articles:
        l = []
        title = a.findAll('a', {'class':'subject_link'})[0].text
        user_id = mod_user_id(a.findAll('span', {'class':'writer'})[0].text)
        article_link = a.findAll('a', {'class':'subject_link'})[0].get('href')
        # print(article_link)
        article_id = re.search(r'(\d{8})', article_link).group()
        article_link = base_url + article_id # 링크에서 검색어 나오지 않게 수정
        reply_num = mod_reply(a)
        view_num = re.search(r'[0-9]+', a.find('span', {'class':'hit'}).text).group()
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
        l.append(reply_num)
        l.append(view_num)
        a_list.append(l)
        time.sleep(.5)

    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result['date_time'] = pd.to_datetime(result['date_time'])
    # 루리웹 도배글 삭제
    result = result[~result['title'].str.contains('주식아') & ~result['title'].str.contains('주식이')]
    result.set_index('article_id')

    return(result)

