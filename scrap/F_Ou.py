# 2017.06.06

import time, random
from urllib.request import urlopen
import utils
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


# cleansing a article title
def mod_title(char):
    result = re.sub(r' [[0-9]*]', '', char)
    return result


# 리플 개수 추출 함수
def mod_reply(char):
    try:
        result = re.search(r'\[[0-9]\]', char).group()
        return re.search(r'[0-9]', result).group()
    except:
        return '0'


# 감동스토리 게시글 수집/판단 함수
def touch_article(conn, url, tears):
    resp = conn.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    del resp
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    base_url = 'http://starboard.kr/todayhumor'
    search_url = 'http://starboard.kr/conn/board/search'
    # Get a html
    s = utils.sess('http://starboard.kr/')
    payload = {'search_text':url}
    resp = s.post(search_url, data=payload)
    articles = soup.find_all('div', attrs={'class': 'ItemContent Discussion'})
    utils.print_log(verbose, "articles cnt", len(articles))
    # 게시글이 없는 경우 리턴
    if len(articles) == 0:
        s.close()
        return pd.DataFrame()
    
    a_list = []
    for a in articles:
        l = []
        title = mod_title(a.find('div', attrs={'class': 'Title'}).find('a').text)
        utils.print_log(verbose, "1 article title", title)
        user_id = ''
        try:
            article_link = a.find('div', attrs={'class': 'Title'}).find('a')['href']
            utils.print_log(verbose, "2 article link", article_link)
        except:
            return pd.DataFrame()
        # print(article_link)
        article_id = re.search(r's_no=(\d+)', article_link).group(1)
        utils.print_log(verbose, "3 article id", article_id)
        date = a.find('time')['datetime']
        utils.print_log(verbose, "4 article date", date)
        content = ''
        try:
            reply_num = re.search(r'\[([0-9]+)\]', title).group(1)
        except:
            reply_num = '0'
        utils.print_log(verbose, "5 article reply cnt", reply_num)
        view_num = a.select_one('div.Meta.Meta-Discussion > span.MItem.MCount.ViewCount').text
        utils.print_log(verbose, "6 article view cnt", view_num)
        user_id = ''
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(s, article_link, tears)
            if not yn:
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
        utils.print_log(verbose, "article line 1", l)
        time.sleep(random.randint(17, 41))
        
    if len(a_list) == 0:  # 감동 주제일 경우 적합 게시물이 없을 경우 빈 DF 반환
        s.close()
        return pd.DataFrame()

    s.close()
    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')
    
    return result
