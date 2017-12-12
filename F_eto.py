# 2017.06.23

import time
from urllib.request import urlopen
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
    AGENT = 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    REFERER = 'http://etorrent.co.kr/'
    
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)

# 게시글 수집
def get_article(url):
    base_url = 'http://etorrent.co.kr/plugin/mobile/'
    # Get a html
    resp = urlopen(url)
    soup = BeautifulSoup(resp, 'html.parser')
    articles = soup.findAll('li', {'class':'subject'})
    # 게시글이 없으면 리턴
    if len(articles) <= 1:
        return(pd.DataFrame())

    a_list = []
    for a in articles:
        l = []
        title = mod_title(a.find('div').text)
        user_id = mod_user_id(a.find('span', {'class':'name'}).text)
        article_link = base_url + a.find('a')['href']
        article_id = re.search(r'\d{3,}', article_link).group()
        reply_num = mod_reply(a.find('div').text)
        view_num = re.search(r'[0-9]+', a.findAll('span', {'class':'datetime'})[1].text).group()
        # Gathering the cotent of each article
        con = urlopen(article_link)
        temp = BeautifulSoup(con, 'html.parser')
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
