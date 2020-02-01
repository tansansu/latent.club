# 2017.06.22

import time, random
from urllib.request import urlopen
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


# 리플 수 추출하는 함수
def mod_reply(char):
    try:
        return char.find('em').text
    except:
        return '0'


# 감동스토리 게시글 수집/판단 함수
def touch_article(url, tears):
    resp = urlopen(url)
    soup = BeautifulSoup(resp, 'lxml')
    ## ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    base_url = 'http://www.82cook.com/entiz/read.php?bn=15&num='
    resp = urlopen(url)
    soup = BeautifulSoup(resp, 'lxml')
    articles = soup.find_all('tr')[1:]
    utils.print_log(verbose, "articles cnt", len(articles))
    # 게시글이 없으면 리턴
    if (len(articles) == 0) | (articles[0].find('td', {'class': 'title'}) is None):
        del resp
        return pd.DataFrame()

    # 게시글 정보 추출
    a_list = []
    for a in articles:
        l = []
        # 검색결과가 없는 경우 예외 처리
        if a.find('td', {'class':'title'}) is None:
            continue

        title = a.find('td', {'class': 'title'}).find('a').text
        user_id = a.find('td', {'class': 'user_function'}).text
        article_link = a.find('a')['href']
        article_id = re.search(r'\d{6,}', article_link).group()
        article_link = base_url + article_id
        date = a.find('td', {'class': 'regdate'})['title']
        content = ''
        reply_num = mod_reply(a)
        view_num = a.find_all('td', {'class':'numbers'})[2].text.replace(',', '')
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(article_link, tears)
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
        time.sleep(random.randint(2, 7) / 3)

    if len(a_list) == 0: # 감동 주제일 경우 적합 게시물이 없을 경우 빈 DF 반환
        del resp
        return pd.DataFrame()

    del resp
    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return result
