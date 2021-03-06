# 2018.01.04

import time, random
import utils
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime


def mod_char(char, for_title=None):
    if for_title:
        try:
            remove_char = re.search(r'\[.*\] *', char).group()
            return char.replace('\n', '').replace('\t', '').replace(remove_char, '')
        except:
            pass
    return char.replace('\n', '').replace('\t', '')


def mod_reply(char):
    try:
        return char.replace('[', '').replace(']', '')
    except:
        return '0'


# 감동스토리 게시글 수집/판단 함수
def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 함수: 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    base_url = 'http://www.ddanzi.com/index.php?m=1&document_srl='

    # 사이트에서 html 가져오기
    s = utils.sess('http://www.ddanzi.com/')
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.select('table > tbody')[1]
    articles_total = table.select('tr')
    # 공지글 제거
    articles = []
    for article in articles_total:
        try:
            if article['class'][0] == 'notice':
                continue
        except:
            articles.append(article)
    utils.print_log(verbose, "articles cnt", len(articles))
    # 게시글이 없는 경우 빈 데이터 프레임 리턴
    if len(articles) == 0:
        return pd.DataFrame()

    # 추출 요소
    a_list = []
    # print(len(articles))
    for a in articles:
        l = []
        title = mod_char(a.select_one('td.title > a').text, 'for_title')
        # print(title)
        article_id = re.search(r'(\d{9})', a.find('a')['href']).group()
        # print(article_link)
        article_link = base_url + article_id
        try:  # 리플수가 없을 경우에 발생하는 None type error
            reply_num = mod_reply(a.find('span', {'class': 'talk'}).text)
        except:
            reply_num = '0'
        # 날짜를 구하기 위해 게시글 클릭
        cont = BeautifulSoup(s.get(article_link).text, 'html.parser')
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(cont, tears)
            if not yn:
                continue
        temp = cont.find('div', {'class': 'right'})
        user_id = mod_char(temp.find('a').text)
        view_num = cont.find('span', {'class': 'read'}).text
        date = cont.find('p', {'class': 'time'}).text
        if len(date) < 9:
            date = str(datetime.now()).split(' ')[0] + ' ' + date
        else:
            date = date.replace('.', '-')

        content = ''
        # 추출항목 리스트로 생성
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
        s.close()
        return pd.DataFrame()

    s.close()  # close Session
    # 결과 데이터 프레임 생성
    result = pd.DataFrame(a_list)
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    # Excepting the particular articles by '펌쟁이'
    result = result[result['member_id'] != '펌쟁이']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return result
