# 2017.01.30
import pandas as pd
import sqlite3
import sys
import time
sys.path
sys.path.insert(0, 'latent_info/')
import F_Clien
import F_Ddan
import F_Ruli
import F_Mlb
import F_HumorU
import F_Etorrent
import F_Ppom
import F_Slr


# 함수: md 파일에 header와 footer 추가하는 함수
def make_pageview_comment(md, category, foot_padding):
    # 헤더 생성
    if category == '부동산':
        meta = '---\ntitle: ' + category + '\nweight: 10\n---\n\n'
    elif category == '찌라시':
        meta = '---\ntitle: ' + category + '\nweight: 20\n---\n\n'
    # md 파일에 추가
    with open(md, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(meta.rstrip('\r\n') + '\n' + content + '\n' + foot_padding)



# 함수: 데이터 프레임을 markdown파일로 변환
def to_md(dataframe, category, directory, page_num):
    dataframe = dataframe[['site', 'title', 'article_link', 'date_time']]
    # 시간 컬럼 수정 : yyyy-mm-dd => mm-dd
    dataframe['date_time'] = dataframe['date_time'].str.replace('\d{4}-', '').str.replace(':\d{2}$', '')
    # 제목에 '[' 또는 ']' 있는 경우 '<', '>'로 변환
    dataframe['title'] = dataframe['title'].str.replace('[', '<').str.replace(']', '>')
    # 링크와 제목 합치기
    temp = '[' + dataframe['title'] + '](' + dataframe['article_link'] + ')'
    # 데이터 프레임 재조립
    dataframe = pd.DataFrame({'사이트':dataframe['site'], '제목':temp,
    '날짜':dataframe['date_time']})
    dataframe = dataframe[['사이트', '제목', '날짜']]
    # 첫줄에 md파일의 테이블 문법 생성
    line = pd.DataFrame([[':---', ] * len(dataframe.columns)], columns=dataframe.columns)
    result = pd.concat([line, dataframe])

    # footer(더보기) 추가하기 위한 html코드
    html_code_page = '/"><center><b><font color="darkblue" size=4><i class="icon icon-download"></i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;더 보기&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i class="icon icon-download"></i></font></b></center></a>'
    # md 파일로 데이터 프레임 저장
    if page_num == 3:
        md = directory + '/page' + str(page_num) + '.md'
        result.to_csv(md, sep='|', index=False)
        # 3번째 페이지는 더보기가 없음
        foot_padding = '<center><b><font color="darkgray" size=4>마지막 페이지 입니다</font></b></center>'
        make_pageview_comment(md, category, foot_padding)
    elif page_num == 2:
        md = directory + '/page' + str(page_num) + '.md'
        result.to_csv(md, sep='|', index=False)
        # 마지막 더보기 문구
        foot_padding = '<a href="../page' + str(page_num+1) + html_code_page
        make_pageview_comment(md, category, foot_padding)
    else:
        md = directory + '/index.md'
        result.to_csv(md, sep='|', index=False)
        # 마지막 더보기 문구
        foot_padding = '<a href="page' + str(page_num+1) + html_code_page
        make_pageview_comment(md, category, foot_padding)


# 함수: 수집한 게시글이 db에 저장된 게시글과 중복인지 확인
def compare_article(category, site, dataframe):
    # 중복 게시글 제거
    try:
        dataframe.drop_duplicates('article_id', keep='first', inplace=True)
        dataframe.drop_duplicates('title', keep='first', inplace=True)
    except:
        pass
    # db에서 게시물 추출
    conn = sqlite3.connect('/Users/tansansu/Google Drive/Python/latent_info/board.db')
    query = 'select article_id from ' + category + ' where site = "' + site + \
    '" order by date_time desc limit 70;'
    temp = pd.read_sql_query(query, conn)
    conn.close()
    try:
        for a in dataframe['article_id']:
            if any(temp['article_id'].str.contains(a)):
                dataframe = dataframe[dataframe['article_id'] != a]
    except:
        pass
    return(dataframe)



# 함수: 스크랩한 게시물 db에 저장
def store_db(subject, site, dataframe):
    # 수집한 게시물이 db에 이미 있는 것인지 비교
    new_d = compare_article(subject, site, dataframe)
    if len(dataframe) != 0:
        ## 신규 자료는 DB에 저장
        conn = sqlite3.connect('/Users/tansansu/Google Drive/Python/latent_info/board.db')
        new_d.to_sql(subject, conn, if_exists='append', index=False)
        conn.close()



# 함수: 사이트 스크래핑
def scrapper(site, url):
    ## 결과로 리턴할 데이터프레임 생성
    result = pd.DataFrame()
    if site == '클리앙':
        for u in url:
            temp = F_Clien.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            # 1초 지연
            time.sleep(1)
        result['site'] = site
    elif site == '딴지일보':
        for u in url:
            temp = F_Ddan.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            time.sleep(1)
        result['site'] = site
    elif site == '루리웹':
        for u in url:
            temp = F_Ruli.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            time.sleep(1)
        result['site'] = site
    elif site == '엠팍':
        for u in url:
            temp = F_Mlb.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            time.sleep(1)
        result['site'] = site
    elif site == '웃대':
        for u in url:
            temp = F_HumorU.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            time.sleep(1)
        result['site'] = site
    elif site == '이토렌트':
        for u in url:
            temp = F_Etorrent.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            time.sleep(1)
        result['site'] = site
    elif site == '뽐뿌':
        for u in url:
            print(u)
            temp = F_Ppom.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            time.sleep(1)
        result['site'] = site
    elif site == 'SLR':
        for u in url:
            print(u)
            temp = F_Slr.get_article(url[u])
            temp['keyword'] = u
            result = result.append(temp)
            time.sleep(1)
        result['site'] = site

    return(result)
