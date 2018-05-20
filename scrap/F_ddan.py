# 2018.01.04

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

def mod_char(char, for_title=None):
    if for_title:
        try:
            remove_char = re.search(r'\[.*\] *', char).group()
            return(char.replace('\n', '').replace('\t', '').replace(remove_char, ''))
        except:
            pass
    return(char.replace('\n', '').replace('\t', ''))

def mod_reply(char):
    try:
        return(char.replace('[', '').replace(']', ''))
    except:
        return('0')


# 함수: 게시글 수집
def get_article(url):
    base_url = 'http://www.ddanzi.com/free/'
    # 사이트에서 html 가져오기
    s = sess()
    s_result = s.get(url)
    soup = BeautifulSoup(s_result.text, 'html.parser')
    articles = soup.findAll('div', {'class':'titleBox'})
    # 게시글이 없는 경우 빈 데이터 프레임 리턴
    if len(articles) == 0:
        return(pd.DataFrame())
    # 공지글 제거
    articles = [x for x in articles if x.find('strong') == None]
    # 게시글이 없는 경우 빈 데이터 프레임 리턴
    if len(articles) == 0:
        return(pd.DataFrame())

    # 추출 요소
    a_list = []
    #print(len(articles))
    for a in articles:
        l = []
        title = mod_char(a.find('div', {'class':'title'}).text, 'for_title')
        #print(title)
        article_id = re.search(r'(\d{9})', a.find('a')['href']).group()
        # print(article_link)
        article_link = base_url + article_id
        try: # 리플수가 없을 경우에 발생하는 None type error
            reply_num = mod_reply( a.find('span', {'class':'talk'}).text)
        except:
            reply_num = '0'
        # 날짜를 구하기 위해 게시글 클릭
        cont = BeautifulSoup(s.get(article_link).text, 'html.parser')
        temp = cont.find('div', {'class':'right'})
        user_id = mod_char(temp.find('a').text)
        view_num = cont.find('span', {'class':'read'}).text
        date = cont.find('p', {'class':'time'}).text
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
