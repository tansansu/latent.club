# 2017.06.06

import time
from urllib.request import urlopen
import requests
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


# cleansing a article title
def mod_title(char):
    result = re.sub(r' [[0-9]*]', '', char)
    return(result)

# 리플 개수 추출 함수
def mod_reply(char):
    try:
        result = re.search(r'\[[0-9]\]', char).group()
        return(re.search(r'[0-9]', result).group())
    except:
        return('0')

# 함수: 세션생성
def sess():
    AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
    REFERER = 'http://m.todayhumor.co.kr/'
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)


# 게시글 수집
def get_article(url):
    base_url = 'http://m.todayhumor.co.kr/'
    # Get a html
    s = sess()
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    articles = soup.findAll('a', {'href':re.compile('view.php?.*')})
    # 게시글이 없는 경우 리턴
    if len(articles) == 0:
        return(pd.DataFrame())

    a_list = []
    for a in articles:
        l = []
        title = mod_title(a.find('h2', {'class':'listSubject'}).text)
        user_id = ''
        try:
            article_link = base_url + a.get('href')
        except:
            return(pd.DataFrame())
        # print(article_link)
        article_id = a.find('span', {'class':'list_no'}).text
        date = a.find('span', {'class':'listDate'}).text.replace('/', '-')
        content = ''
        reply_num = mod_reply(a.find('h2', {'class':'listSubject'}).text)
        view_num = a.find('span', {'class':'list_viewCount'}).text

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
        
    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')
    
    return(result)
