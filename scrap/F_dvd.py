# 2018.05.05

import time, random
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


# 함수: 세션생성
def sess():
    AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
    REFERER = 'https://dvdprime.com/'
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return s


# Modifing user_ids
def mod_user_id(char):
    result = char.replace(" ", '').replace('\r', '').replace('\n', '').replace('\t', '')
    return result


# 날짜 string 수정 함수
def mod_date(char):
    result = re.search(r'\d{4}.+', char).group()
    result = result.replace("\t", '')
    return result


# 감동스토리 게시글 수집/판단 함수
def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears


# 게시글 수집
def get_article(url, subject, tears=15):
    base_url = 'https://dvdprime.com/g2/bbs/board.php?bo_table=comm&wr_id='
    # Get a html
    s = sess()
    s_result = s.get(url)
    soup = BeautifulSoup(s_result.text, 'html.parser')
    # Extracting articles from the html
    articles = soup.findAll('a', {'class': 'list_subject_a'})

    if len(articles) == 0:
        s.close()
        return pd.DataFrame()

    # Extracting elements from articles
    a_list = []
    for a in articles:
        l = []
        try:
            title = a.find('span', {'class': 'list_subject_span_pc'}).text
        except:
            continue
        # print(title)
        article_id = re.search(r'(\d{8})', a['href']).group()
        if a.find('em'):
            reply_num = a.find('em').text
        else:
            reply_num = '0'
        article_link = base_url + article_id
        # 게시글 내용 가져오기
        content = BeautifulSoup(s.get(article_link).text, 'html.parser')
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(content, tears)
            if not yn:
                continue
        user_id = mod_user_id(content.find('span', {'class': 'member'}).text)
        view_num = re.search(r'[0-9]+', content.find('div', {'id': 'view_hit'}).text).group()
        # Gathering the cotent of each article
        date = mod_date(content.find('div', {'id': 'view_datetime'}).text)
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
        time.sleep(random.randint(2, 7) / 3)

    if len(a_list) == 0: # 감동 주제일 경우 적합 게시물이 없을 경우 빈 DF 반환
        s.close()
        return pd.DataFrame()

    s.close()
    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result['date_time'] = pd.to_datetime(result['date_time'])

    return result

