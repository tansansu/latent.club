# 2018.01.07

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
    # html table code
    html_table = "<table>\n"
    html_title = "<tr class='title_link'>"
    html_info = "<tr class='title_info'>"
    # 사이트명에 다른 컬러를 입히기 위한 사이트-컬러명 dictionary
    with open('db/site_col.json', 'r') as f:
        site_col = json.load(f)
        
    content = '\n' + html_table
    for i in range(len(dataframe)):
        # 제목 줄 생성
        con_title = "<td><a href='" + dataframe.iloc[i]['article_link'] + "'>" + \
        dataframe.iloc[i]['title'] + "</a></td></tr>\n"
        # 제목 줄에 html 코드 추가
        content += html_title + con_title
        # 사이트명, 날짜_시간 정보 줄 생성
        ## 사이트명의 너비를 10칸으로 고정하고 양쪽에 빈공간 생성
        site_width = len(dataframe.iloc[i]['site'])
        if (site_width == 6):
            site_name = ('&nbsp;' * 4) + dataframe.iloc[i]['site'] + ('&nbsp;' * 4)
        elif site_width == 4:
            site_name = ('&nbsp;' * 3) + dataframe.iloc[i]['site'] + ('&nbsp;' * 3)
        elif (site_width == 3) & (dataframe.iloc[i]['site'] != 'SLR'):
            site_name = ('&nbsp;' * 5) + dataframe.iloc[i]['site'] + ('&nbsp;' * 5)
        elif site_width == 2:
            site_name = ('&nbsp;' * 7) + dataframe.iloc[i]['site'] + ('&nbsp;' * 7)
        elif dataframe.iloc[i]['site'] == 'SLR':
            site_name = ('&nbsp;' * 7) + dataframe.iloc[i]['site'] + ('&nbsp;' * 8)
        else:
            site_name = ('&nbsp;' * 7) + dataframe.iloc[i]['site'] + ('&nbsp;' * 7)
        # 정보 표시줄(사이트명, 날짜_시간) 생성, 날짜_시간은 분까지만 표시되게 함
        if dataframe.iloc[i]['view_num'] is None:
            dataframe.iloc[i]['view_num'] = '  -  '
        if dataframe.iloc[i]['reply_num'] is None:
            dataframe.iloc[i]['reply_num'] = ' - '
            
        con_info = '<td><span class="' + site_col[dataframe.iloc[i]['site']] + '">' + \
        site_name + '</span>&nbsp;&nbsp;&nbsp;' + dataframe.iloc[i]['date_time'][:-3] + '&nbsp;&nbsp;' + \
        '<span class="view">' + dataframe.iloc[i]['view_num'] + '</span>&nbsp;&nbsp;<span class="reply">[' + \
        dataframe.iloc[i]['reply_num'] + ']</span></td></tr>\n'
        # 정보 줄에 html 코드 삽입
        content += html_info + con_info

    content += "</table>\n\n"

    # footer(더보기) 추가하기 위한 html코드
    html_code_page = '/"><center><b><font color="darkblue" size=4><i class="icon icon-download"></i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;더 보기&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i class="icon icon-download"></i></font></b></center></a>'
    # 함수: md 파일에 header와 footer 추가하는 함수
    def make_pageview_comment(md, category, foot_padding):
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
        elif category == '트윗/페북':
            meta = '---\ntitle: ' + category + '\nweight: 60\n---\n\n'
        # md 파일에 추가
        with open(md, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(meta.rstrip('\r\n') + '\n' + content + '\n' + foot_padding)

    # md 파일로 데이터 프레임 저장
    if page_num == 3:
        md = directory + '/page' + str(page_num) + '.md'
        # 최종 md 파일 생성
        with open(md, 'w') as f:
            f.write(content)
        # 3번째 페이지는 더보기가 없음
        foot_padding = '<center><b><font color="darkgray" size=4>마지막 페이지 입니다</font></b></center>'
        make_pageview_comment(md, category, foot_padding)
    elif page_num == 2:
        md = directory + '/page' + str(page_num) + '.md'
        # 최종 md 파일 생성
        with open(md, 'w') as f:
            f.write(content)
        # 마지막 더보기 문구
        foot_padding = '<a href="../page' + str(page_num+1) + html_code_page
        make_pageview_comment(md, category, foot_padding)
    else:
        md = directory + '/index.md'
        # 최종 md 파일 생성
        with open(md, 'w') as f:
            f.write(content)
        # 마지막 더보기 문구
        foot_padding = '<a href="page' + str(page_num+1) + html_code_page
        make_pageview_comment(md, category, foot_padding)


# 함수: 수집한 게시글이 db에 저장된 게시글과 중복인지 확인
def compare_article(category, site, dataframe):
    # 중복 게시글 제거
    try:
        dataframe.drop_duplicates('article_id', inplace=True)
        dataframe.drop_duplicates('title', inplace=True)
    except:
        pass
    # db에서 게시물 추출
    conn = sqlite3.connect('db/board.db')
    query = 'select article_id from ' + category + ' where site = "' + site + \
    '" order by date_time desc limit 300;'
    temp = pd.read_sql_query(query, conn)
    conn.close()
    try:
        dataframe = dataframe[~dataframe['article_id'].isin(temp['article_id'])]
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
