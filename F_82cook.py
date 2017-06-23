# 2017.06.22

import time
from urllib.request import urlopen
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


# 리플 수 추출하는 함수
def mod_reply(char):
    try:
        return(char.find('em').text)
    except:
        return('0')

# 게시글 수집
def get_article(url):
    base_url = 'http://www.82cook.com/entiz/'
    resp = urlopen(url)
    soup = BeautifulSoup(resp, 'html.parser')
    articles = soup.findAll('tr')[1:]

    a_list = []
    for a in articles:
        l = []

        title = a.find('td', {'class':'title'}).find('a').text
        user_id = a.find('td', {'class':'user_function'}).text
        article_link = base_url + a.find('a')['href']
        article_id = re.search(r'(\d{7})', article_link).group()
        date = a.find('td', {'class':'regdate'})['title']
        content = ''
        reply_num = mod_reply(a)
        view_num = a.find('td', {'class':'numbers'}).text
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
