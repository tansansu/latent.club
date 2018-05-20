# 2018.02.03

import time
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime

# Modifing user_ids
def mod_title(char):
    result = re.sub(r'(\([^()]*\))', '', char).replace('\xa0', '').replace('\t', '')
    return(result)

def mod_user_id(char):
    result = re.sub(r' +', '', char)
    return(result)

def mod_date(char):
    result = re.sub(r' \([^()]\)', '', char)
    return(result)

def mod_reply(char):
    try:
        return(re.search(r'[0-9]+', re.search(r'\([0-9]+\)', char).group()).group())
    except:
        return('0')

# Session
def sess():
    AGENT = 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36'
    REFERER = 'http://www.etoland.co.kr/'    
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)

# 게시글 수집
def get_article(url):
    base_url = 'http://www.etoland.co.kr/plugin/mobile/board.php?bo_table=etoboard&wr_id='
    # Get a html
    s = sess()
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    articles = soup.findAll('li', {'class':'subject'})
    # 게시글이 없으면 리턴
    if len(articles) == 0:
        return(pd.DataFrame())

    a_list = []
    for a in articles:
        l = []
        title = mod_title(a.find('div').text)
        try:
            user_id = mod_user_id(a.find('span', {'class':'name'}).text)
        except:
            continue
        article_id = re.search(r'\d{3,}', a.find('a')['href']).group()
        article_link = base_url + article_id
        reply_num = mod_reply(a.find('div').text)
        view_num = re.search(r'[0-9]+', a.findAll('span', {'class':'datetime'})[1].text).group()
        # Gathering the cotent of each article
        con = s.get(article_link)
        temp = BeautifulSoup(con.text, 'html.parser')
        try:
            '''
            content = temp.cssselect('td.mw_basic_view_content')[0].\
            cssselect('div[id="view_content"]')[0].text_content()
            '''
            content = ''
            date = mod_date(temp.find('span', {'class':'write_date'}).text)
            if temp.find('span', {'class':'write_date'}).text == date:
                continue
        except:
            continue

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