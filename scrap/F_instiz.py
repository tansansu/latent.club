# 2018.05.05

import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd


# 함수: 세션생성
def sess():
    AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
    REFERER = 'https://www.instiz.net/'
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    return(s)

# Modifing user_ids
def mod_user_id(char):
    result = char.replace(" ", '').replace('\r', '').replace('\n', '').replace('\t', '')
    return(result)


# Modifing user_ids
def mod_view_num(char):
    result = re.search(r'회.+', char).group()
    result = result.replace('회 ', '')
    return(result)


# 게시글 수집
def get_article(url):
    base_url = 'https://www.instiz.net/pt?no='
    # Get a html
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    # Extracting articles from the html
    articles = soup.findAll('span', {'id':'subject'})
    
    if len(articles) == 0:
        return(pd.DataFrame())

    # Extracting elements from articles
    a_list = []
    for a in articles:
        l = []
        title = a.text
        article_id = re.search(r'(\d{7})', a.find('a')['href']).group()
        article_link = base_url + article_id
        ## 게시글 내용 가져오기
        content = BeautifulSoup(urlopen(article_link), 'html.parser')
        user_id = mod_user_id(content.find('span', {'itemprop':'publisher'}).text)
        view_num = mod_view_num(content.find('div', {'class':'tb_left'}).text)
        if a.find('a', {'id':'view_cmt'}):
            reply_num = a.find('a', {'id':'view_cmt'}).text
        else:
            reply_num = '0'
        # Gathering the cotent of each article
        date = content.find('span', {'itemprop':'datePublished'})['title']
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
        time.sleep(.5)

    result = pd.DataFrame(a_list)
    # munging of the dataframe
    result.columns = ['title', 'date_time', 'article_id', 'member_id', 'article_link', 'content', 'reply_num', 'view_num']
    result['date_time'] = pd.to_datetime(result['date_time'])

    return(result)

