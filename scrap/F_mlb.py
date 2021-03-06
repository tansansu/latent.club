# 2017.05.13

import time, random
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import utils
import pandas as pd
from datetime import datetime


def mod_reply(char):
    try:
        return(char.find('span', {'class': 'replycnt'}).text
            .replace('[', '').replace(']', '').replace(',', ''))
    except:
        return '0'


# 감동스토리 게시글 수집/판단 함수
def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    # Get a html
    resp = urlopen(url)
    soup = BeautifulSoup(resp, 'lxml')
    articles = soup.find_all('tr')[1:]
    # 게시글만 추출
    articles = [a for a in articles if a.find('td', {'class': 't_left'}) is not None]
    utils.print_log(verbose, "articles cnt", len(articles))
    # 게시글이 없으면 리턴
    if len(articles) == 0:
        del resp
        return pd.DataFrame()
    
    a_list = []
    for a in articles:
        l = []
        title = a.find('a')['alt']
        user_id = a.find('span', {'class': 'nick'}).text
        article_link = a.find('a')['href']
        article_link = article_link.replace(re.search(r'&query=.+&', article_link).group(), '&')
        article_id = re.search(r'(\d{18})', article_link).group()
        reply_num = mod_reply(a)
        view_num = a.find('span', {'class': 'viewV'}).text.replace(',', '')
        if view_num == '':
            continue
        # Gathering the cotent of each article
        con = BeautifulSoup(urlopen(article_link), 'html.parser')
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(con, tears)
            if not yn:
                continue
        date = con.find_all('span', {'class': 'val'})[3].text
        # date = mod_user_id(date)
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
        utils.print_log(verbose, "article line 1", l)
        time.sleep(random.randint(2, 7) / 3)

    if len(a_list) == 0:  # 감동 주제일 경우 적합 게시물이 없을 경우 빈 DF 반환
        del resp
        return pd.DataFrame()

    del resp
    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return result
