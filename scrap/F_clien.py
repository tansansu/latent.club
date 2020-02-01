# 2017.012.12

import time, random
import utils
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime


# Modifing text
def mod_text(char):
    result = re.sub(r'[\n\t]+', '', char)
    #try:
    #    result = result.replace('클리앙 > 모두의공원 > ', '')
    #except:
    #    pass
    return result


# 감동스토리 게시글 수집/판단 함수
def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    base_url = 'https://www.clien.net/service/board/park/'
    # Get a html
    s = utils.sess('https://www.clien.net')
    resp = s.get(url)
    # Extracting articles from the html
    soup = BeautifulSoup(resp.text, 'lxml')
    articles = soup.select('div.list_item')
    utils.print_log(verbose, "articles cnt", len(articles))
    if len(articles) == 0:
        del resp
        return pd.DataFrame()
    # Extracting elements from the html document
    a_list = []
    for a in articles:
        l = []
        try:
            title = mod_text(a.select_one('span.list_subject > a').text)
        except AttributeError:
            continue
        date_time = a.select_one('span.timestamp').text
        #print("datetime", date_time)
        article_link = a.select_one('span.list_subject > a')['href']
        article_id = re.search(r'[0-9]{8}', article_link).group(0)
        article_link = base_url + article_id
        try:
            con = BeautifulSoup(s.get(article_link).text, 'lxml')
            # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
            if subject == 'touching':
                yn = touch_article(con, tears)
                if not yn:
                    continue
            if con.select_one('span.nickname > img') is None:
                member_id = mod_text(con.select_one('span.nickname').text)
            else:
                member_id = con.select_one('span.nickname > img')['alt']
            content = ''
            reply_num = con.select_one('div#comment-point strong').text
            view_num = con.select_one('span.view_count > strong').text
        except Exception as e:
            print(e)
            continue
        l.append(title)
        l.append(date_time)
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
        del resp
        return pd.DataFrame()
    del resp
    result = pd.DataFrame(a_list)
    # 데이터 프레임 컬럼 생성
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'].tolist())
    result.set_index('article_id')
    return result
