# 2017.01.30

import time
import requests
import urllib
import re
import pandas as pd
from datetime import datetime
from lxml import html

# 함수: 세션생성
def sess():
    AGENT = 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    REFERER = 'http://www.ddanzi.com/'

    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)


# 함수: 게시글 수집
def get_article(url):
    # 사이트에서 html 가져오기
    s = sess()
    s_result = s.get(url)

    # html에서 게시글 부분만 추출
    elem = html.fromstring(s_result.text)
    articles = elem.cssselect('ul.searchResult')[0].cssselect('li')
    # 게시글이 없는 경우 빈 데이터 프레임 리턴
    if len(articles) == 0:
        return(pd.DataFrame())

    # 추출 요소
    a_list = []
    for a in articles:
        l = []
        title = a.cssselect('dl')[0].cssselect('dt')[0].cssselect('a')[0].text_content()
        user_id = a.cssselect('address')[0].cssselect('strong')[0].text_content()
        article_link = a.cssselect('a')[0].get('href').strip()
        # print(article_link)
        article_id = re.search(r'(\d{9})', article_link).group()
        date = a.cssselect('address')[0].cssselect('span')[0].text_content()
        # 게시글 제목 클릭해서 내용 html 수집
        con = s.get(article_link)
        temp = html.fromstring(con.text)
        # 수집 내용 없을 경우 pass
        try:
            content = temp.cssselect('div.content')[0].cssselect('div.bd')[0].\
            cssselect('div.co')[0].text_content()
        except:
            content = a.cssselect('dl')[0].cssselect('dd')[0].text_content()
        # 추출항목 리스트로 생성
        l.append(title)
        l.append(date)
        l.append(article_id)
        l.append(user_id)
        l.append(article_link)
        l.append(content)
        a_list.append(l)
        time.sleep(.5)

    # 결과 데이터 프레임 생성
    result = pd.DataFrame(a_list)
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content']
    ## Excepting the particular articles by '펌쟁이'
    result = result[result['member_id'] != '펌쟁이']
    result['date_time'] = pd.to_datetime(result['date_time'])
    result.set_index('article_id')

    return(result)
