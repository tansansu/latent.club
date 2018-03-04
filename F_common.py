# 2018.01.07

#import pdb
import pickle
import json
import pandas as pd
import sqlite3
import requests
import sys
import time
sys.path
sys.path.insert(0, 'latent_info/')
import F_clien
import F_ddan
import F_ruli
import F_mlb
import F_Ou
import F_eto
import F_ppom
import F_slr
import F_82cook
import F_inven


# 함수: 데이터 프레임을 markdown파일로 변환
def to_md(dataframe, category, directory, page_num):
    dataframe.reset_index(drop=True, inplace=True)    
    # 함수: md 파일에 hugo header를 추가하는 함수
    def make_pageview_comment(category):
        # 헤더 생성
        if category == '부동산':
            meta = '---\ntitle: ' + category + '\nweight: 10\n---\n\n'
        elif category == '주식':
            meta = '---\ntitle: ' + category + '\nweight: 20\n---\n\n'
        elif category == '경제':
            meta = '---\ntitle: ' + category + '\nweight: 30\n---\n\n'
        elif category == '찌라시':
            meta = '---\ntitle: ' + category + '\nweight: 40\n---\n\n'
        elif category == '가상화폐':
            meta = '---\ntitle: ' + category + '\nweight: 50\n---\n\n'
        elif category == '트윗':
            meta = '---\ntitle: ' + category + '\nweight: 60\n---\n\n'        
        return(meta)

    # 콘텐트에 헤더와 html헤더 추가
    content = make_pageview_comment(category) + '\n<table>\n'

    # 게시글 table tag
    html_title = "<tr class='title_link'>"
    html_info = "<tr class='title_info'>"
    # 사이트명에 다른 컬러를 입히기 위한 사이트-컬러명 dictionary
    with open('db/site_col.json', 'r') as f:
        site_col = json.load(f)
    for i in range(len(dataframe)):
        # 제목 줄 생성
        con_title = '<td colspan="2"><a href="%s">%s</a></td></tr>\n' % \
        (dataframe.loc[i, 'article_link'], dataframe.loc[i, 'title'])
        # 제목 줄에 html 코드 추가
        content += html_title + con_title
        # 사이트명, 날짜_시간 정보 줄 생성
        ## 사이트명 생성
        site_name = "<td width='55px' class=" + site_col[dataframe.loc[i, 'site']] + \
        ">%s</td>" % dataframe.loc[i, 'site']
        ## 정보 표시줄(사이트명, 날짜_시간) 생성, 날짜_시간은 분까지만 표시되게 함
        ## 뷰 수나 리플 수가 없을 때 예외 처리
        if dataframe.loc[i, 'view_num'] is None:
            dataframe.loc[i, 'view_num'] = '  -  '
        if dataframe.loc[i, 'reply_num'] is None:
            dataframe.loc[i, 'reply_num'] = ' - '
        con_info = '<td>&nbsp;&nbsp;&nbsp;%s&nbsp;&nbsp;<span class="view">%s</span>&nbsp;&nbsp;<span class="reply">[%s]</span></td></tr>\n' % \
        (dataframe.loc[i, 'date_time'][:-3], dataframe.loc[i, 'view_num'], dataframe.loc[i, 'reply_num'])
        # 정보 줄에 html 코드 삽입
        content += html_info + site_name + con_info
    content += "</table>"

    # page footer
    ## footer에 페이지 인덱스 추가하기 위한 html 코드
    foot_table = '<center><span class="foot_index">'

    if page_num == 1:
        page = '/index'
        page1_link = page1_link_end = ' '
        page2_link = '<a href="./page2">'; page2_link_end = '</a>'
        page3_link = '<a href="./page3/">'; page3_link_end = '</a>'
    elif page_num == 2:
        page = '/page2'
        page2_link = page2_link_end = ' '
        page1_link = '<a href="../">'; page1_link_end = '</a>'
        page3_link = '<a href="../page3/">'; page3_link_end = '</a>'
    elif page_num == 3:
        page = '/page3'
        page3_link = page3_link_end = ' '
        page1_link = '<a href="../">'; page1_link_end = '</a>'
        page2_link = '<a href="../page2/">'; page2_link_end = '</a>'

    foot_1 = '<td>%s [ 1 - 60 ] %s</td>' % (page1_link, page1_link_end)
    foot_2 = '<td>%s [ 61 - 120 ] %s</td>' % (page2_link, page2_link_end)
    foot_3 = '<td>%s [ 121 - 180 ] %s</td></tr></span></center>\n' % (page3_link, page3_link_end)

    content += foot_table + foot_1 + foot_2 + foot_3

    # md 파일 저장
    path_md = directory + page + '.md'
    with open(path_md, 'w') as f:
        f.write(content)

# 함수: 수집한 게시글이 db에 저장된 게시글과 중복인지 확인
def compare_article(category, site, dataframe):
    # 중복 게시글 제거
    try:
        dataframe.drop_duplicates('article_id', inplace=True)
        dataframe.drop_duplicates('title', inplace=True)
    except:
        pass
    # db에서 게시물 추출
    with sqlite3.connect('db/board.db') as conn:
        query = 'select article_id from ' + category + ' where site = "' + site + \
        '" order by date_time desc limit 300;'
        temp = pd.read_sql(query, conn)
    try:
        dataframe = dataframe[~dataframe['article_id'].isin(temp['article_id'])]
        dataframe = dataframe[~dataframe['title'].isin(temp['title'])]
    except:
        pass
    return(dataframe)


# 함수: 스크랩한 게시물 db에 저장
def store_db(subject, site, dataframe):
    if dataframe is None:
        return(0)
    # 수집한 게시물이 db에 이미 있는 것인지 비교
    new_d = compare_article(subject, site, dataframe)
    # 수집한 new 게시글
    article_count = new_d.shape[0]
    if article_count >= 1:
        ## 신규 자료는 DB에 저장
        with sqlite3.connect('db/board.db') as conn:
            new_d.to_sql(subject, conn, if_exists='append', index=False)
    # 수집한 new 게시글 개수 리턴
    return(article_count)


# 함수: 사이트 스크래핑
def scrapper(site, urls):
    # 콘텐츠 사이트
    site_link = {'클리앙':'clien', '딴지일보':'ddan', '루리웹':'ruli', \
    '엠팍':'mlb', '오유':'Ou', '이토렌트':'eto', '뽐뿌':'ppom', \
    'SLR':'slr', '82cook':'82cook', '인벤':'inven'}
    # URL 리스트
    url = urls[site_link[site]]
    # 검색어 리스트
    keywords = [x for x in url.keys()]
    # 결과로 리턴할 데이터프레임 생성
    result = pd.DataFrame()
    # 사이트마다 키워드 url 반복
    for u in keywords:
        # 개별 사이트 소스파일의 get_article 함수 실행
        temp = globals()['F_' + site_link[site]].get_article(url[u])
        if temp.shape[0] == 0:
            continue
        temp['keyword'] = u
        result = result.append(temp)
        # 1초 지연
        time.sleep(1)
    result['site'] = site

    return(result)


# 함수: 머신러닝 학습용 샘플데이터 저장
def export_sample(df, object):
    from xlsxwriter.utility import xl_rowcol_to_cell
    writer = pd.ExcelWriter('sample_data/sample_' + object + '_tmp.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='to')


# 제목에 트윗이 표시된 것만 추출하는 함수
def tweet_name_filter(dataframe):
    cond_t1 = dataframe['title'].str.contains('트윗$')
    cond_t2 = dataframe['title'].str.contains('트윗\.')
    cond_t3 = dataframe['title'].str.contains('트위터$')
    cond_t4 = dataframe['title'].str.contains('트위터\.')
    # 페북조건 추가
    cond_f1 = dataframe['title'].str.contains('페북$')
    cond_f2 = dataframe['title'].str.contains('페북\.')
    dataframe = dataframe[cond_t1 | cond_t2 | cond_t3 | cond_t4 | cond_f1 | cond_f2]
    if dataframe.shape[0] == 0:
        return(None)
    else:
        dataframe.loc[:, 'result'] = 'Y'
        return(dataframe)

# 가상화폐에서 코인노래방 게시글은 제외
def coin_name_filter(dataframe):
    condition = dataframe['title'].str.contains('노래방')
    dataframe = dataframe[~condition]
    if dataframe.shape[0] == 0:
        return(None)
    else:
        dataframe.loc[:, 'result'] = 'Y'
        return(dataframe)


def firebase():
    with open('db/firebase.config', 'r') as f:
        config = json.load(f)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    return(db)
