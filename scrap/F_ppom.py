# 2017.06.04

import time, random
from urllib.request import urlopen
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


def mod_reply(char):
    try:
        result = char.find('span', {'class': 'rp'}).text
        return re.search(r'[0-9]+', result).group()
    except:
        return '0'


def mod_view(char):
    try:
        result = re.search(r'\[ [0-9]+', char.find('span', {'class': 'hi'}).text).group()
        return result.replace('[ ', '')
    except:
        return '0'


# 감동스토리 게시글 수집/판단 함수
def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    # url
    base_url = 'http://m.ppomppu.co.kr/new/'
    # Get a html
    resp = urlopen(url)
    soup = BeautifulSoup(resp, 'lxml')
    articles = soup.find_all('ul', {'class':'bbsList'})[0].find_all('li')
    articles = [x for x in articles if not x.find('strike')]
    utils.print_log(verbose, "articles cnt", len(articles))
    # Return empty dataframe if no articles
    if len(articles) == 0:
        del resp
        return pd.DataFrame()

    a_list = []
    for a in articles:
        l = []
        try:  # 삭제된 게시물은 링크가 안남아서 에러가 생김
            article_link = base_url + a.find('a', {'class': 'noeffect'})['href']
            del_keyword = re.search(r'&keyword=.+', article_link).group()
            article_link = article_link.replace(del_keyword, '')
        except:
            continue
        title = a.find('strong').text
        user_id = a.find('span', {'class': 'ct'}).text
        article_id = re.search(r'(\d{7})', article_link).group()
        reply_num = mod_reply(a)
        view_num = mod_view(a)
        # scrapping a date, a time and a content
        try:
            cont = BeautifulSoup(urlopen(article_link, timeout=10), 'html.parser')
        except:
            continue
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(cont, tears)
            if not yn:
                continue
        date = cont.find('span', {'class': 'hi'}).text.replace('  | ', '')
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
