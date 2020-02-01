# 2017.06.22

import time, random
import utils
import urllib
import re
import pandas as pd
from datetime import datetime
from lxml import html
from bs4 import BeautifulSoup


# cleansing a article title
def mod_title(char):
    result = char.replace('\r', '').replace('\n', '').replace('\t', '')
    # Removing a number of replies
    result = re.sub(r"\[[0-9]+\]", '', result)
    return result


# 리플 수 추출하는 함수
def mod_reply(char):
    try:
        result = re.search(r'\[[0-9]+\]', char).group()
        return re.search(r'[0-9]+', result).group()
    except:
        return '0'


def mod_view(char):
    result = re.search(r'조회 [0-9]+', char).group()
    return result.replace('조회 ', '')


def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    base_url = 'http://starboard.kr/slr'
    search_url = 'http://starboard.kr/conn/board/search'
    # Get a html
    s = utils.sess('http://starboard.kr/')
    base = s.get(base_url)
    # s_result.encoding = 'euc-kr' # Revising the encoding
    # Extracting articles from the html
    payload = {'search_text':url}
    resp = s.post(search_url, data=payload)
    soup = BeautifulSoup(resp.text, 'lxml')
    articles = soup.find_all('div', attrs={'class': 'ItemContent Discussion'})
    utils.print_log(verbose, "articles cnt", len(articles))
    if len(articles) == 0:
        s.close()
        return pd.DataFrame()
        
    # print(articles)
    s.close()  # starboard session 종료
    s = utils.sess('http://www.slrclub.com/')
    a_list = []
    for a in articles:
        l = []
        title = mod_title(a.find('div', attrs={'class': 'Title'}).find('a').text)
        utils.print_log(verbose, "1 article title", title)
        try:
            article_link = a.find('div', attrs={'class': 'Title'}).find('a')['href']
            utils.print_log(verbose, "2 article link", article_link)
        except:
            continue
        # print(article_link)
        article_id = re.search(r'(\d{8})', article_link).group()
        utils.print_log(verbose, "3 article id", article_id)
        date = a.find('time')['datetime']
        utils.print_log(verbose, "4 article date", date)
        try:
            reply_num = re.search(r'\[([0-9]+)\]', title).group(1)
        except:
            reply_num = '0'
        utils.print_log(verbose, "5 article reply cnt", reply_num)
        view_num = a.select_one('div.Meta.Meta-Discussion > span.MItem.MCount.ViewCount').text
        utils.print_log(verbose, "6 article view cnt", view_num)
        # Get a content of the article
        con = BeautifulSoup(s.get(article_link).text, 'html.parser')
        # 존재하지 않는 게시물 예외 처리
        if con.find('p', {'class': 'err_msg'}) is not None:
            continue
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(con, tears)
            if not yn:
                continue
        member_id = con.find('span', attrs={'class': 'lop'})
        if member_id is None:
            member_id = ''
        else:
            member_id = con.find('span', attrs={'class': 'lop'}).text

        content = ''
        # Making the list
        l.append(title)
        l.append(date)
        l.append(article_id)
        l.append(member_id)
        l.append(article_link)
        l.append(content)
        l.append(reply_num)
        l.append(view_num)
        a_list.append(l)
        utils.print_log(verbose, "article line 1", l)
        time.sleep(random.randint(2, 7) / 3)

    if len(a_list) == 0:  # 감동 주제일 경우 적합 게시물이 없을 경우 빈 DF 반환
        base.close()
        s.close()
        return pd.DataFrame()

    # 세션 종료
    base.close()
    s.close()

    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'])
    result = result[result['member_id'] != '']
    result.set_index('article_id')

    return result
