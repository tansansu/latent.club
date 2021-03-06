# 2018.02.03

import time, random
import utils
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime


# Modifing user_ids
def mod_title(char):
    result = re.sub(r'(\([^()]*\))', '', char).replace('\xa0', '').replace('\t', '')
    return result


def mod_user_id(char):
    result = re.sub(r' +', '', char)
    return result


def mod_date(char):
    result = re.sub(r' \([^()]\)', '', char)
    return result


def mod_reply(char):
    try:
        return re.search(r'[0-9]+', re.search(r'\([0-9]+\)', char).group()).group()
    except:
        return '0'


# 감동스토리 게시글 수집/판단 함수
def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    base_url = 'http://www.etoland.co.kr/plugin/mobile/board.php?bo_table=etoboard01&wr_id='
    # Get a html
    s = utils.sess('http://www.etoland.co.kr/')
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    articles = soup.find_all('li', {'class': 'subject'})
    utils.print_log(verbose, "articles cnt", len(articles))
    # 게시글이 없으면 리턴
    if len(articles) == 0:
        s.close()
        return pd.DataFrame()

    a_list = []
    for a in articles:
        l = []
        title = mod_title(a.find('div').text)
        try:
            user_id = mod_user_id(a.find('span', {'class': 'name'}).text)
        except:
            continue
        article_id = re.search(r'wr_id=\d+', a.find('a')['href']).group().replace('wr_id=', '')
        article_link = base_url + article_id
        reply_num = mod_reply(a.find('div').text)
        view_num = re.search(r'[0-9]+', a.find_all('span', {'class': 'datetime'})[1].text).group()
        # Gathering the cotent of each article
        con = s.get(article_link)
        temp = BeautifulSoup(con.text, 'html.parser')
        if subject == 'touching':
            yn = touch_article(temp, tears)
            if not yn:
                continue
        try:
            '''
            content = temp.cssselect('td.mw_basic_view_content')[0].\
            cssselect('div[id="view_content"]')[0].text_content()
            '''
            content = ''
            date = mod_date(temp.find('span', {'class': 'write_date'}).text)
            if temp.find('span', {'class': 'write_date'}).text == date:
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
        utils.print_log(verbose, "article line 1", l)
        time.sleep(random.randint(2, 7) / 3)
    if len(a_list) == 0: # 감동 주제일 경우 적합 게시물이 없을 경우 빈 DF 반환
        s.close()
        return pd.DataFrame()

    s.close()
    result = pd.DataFrame(a_list)

    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')
    
    return result
