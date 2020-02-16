# 2017.06.14
import utils
import time, random
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd


# Modifing user_ids
def mod_user_id(char):
    return char.replace(" ", '').replace('\r', '').replace('\n', '').replace('\t', '')


# 날짜 string 수정 함수
def mod_date(char):
    result = "20" + char
    result = result.replace(".", '-').replace('(', '').replace(')', '')
    return result


# 리플수 string 수정 함수
def mod_reply(char):
    try:
        return char.find('span', {'class':'num'}).text
    except:
        return '0'


def touch_article(soup, tears):
    # ㅠ, ㅜ의 개수로 감동스토리 판단
    tear_cnt = soup.text.count('ㅜ') + soup.text.count('ㅠ')
    return tear_cnt >= tears

    
# 게시글 수집
def get_article(url, subject, tears=15, verbose=False):
    base_url = 'http://m.ruliweb.com/community/board/300148/read/'
    # Get a html
    s = utils.sess(base_url)
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    # Extracting articles from the html
    articles = soup.select('tr.table_body')
    articles = [x for x in articles if len(x.get('class')) < 2] # 공지글/베스트 제외
    utils.print_log(verbose, "articles cnt", len(articles))
    # 유동적인 결과없음 글이 있으면 리턴
    if articles[0].find('strong').text == '결과없음':
        return pd.DataFrame()

    # Extracting elements from articles
    a_list = []
    for a in articles:
        l = []
        title = a.find_all('a', {'class': 'subject_link'})[0].text.strip()
        user_id = mod_user_id(a.find_all('span', {'class': 'writer'})[0].text)
        article_link = a.find_all('a', {'class': 'subject_link'})[0].get('href')
        # print(article_link)
        article_id = re.search(r'(\d{8})', article_link).group()
        article_link = base_url + article_id  # 링크에서 검색어 나오지 않게 수정
        reply_num = mod_reply(a)
        view_num = re.search(r'[0-9]+', a.find('span', {'class': 'hit'}).text).group()
        # Gathering the cotent of each article
        resp = s.get(article_link)
        con = BeautifulSoup(resp.text, 'html.parser')
        # 감동 주제일 경우 Y값을 판단해서 Y가 아니면 next loop
        if subject == 'touching':
            yn = touch_article(con, tears)
            if not yn:
                continue
        date = mod_date(con.find('span', {'class': 'regdate'}).text)
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
        return pd.DataFrame()

    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result.loc[:, 'date_time'] = pd.to_datetime(result['date_time'])
    # 루리웹 도배글 삭제
    result = result[~result['title'].str.contains('주식아') & ~result['title'].str.contains('주식이')]
    result.set_index('article_id')

    return result

