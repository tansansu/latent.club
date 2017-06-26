# 2017.06.25

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
        meta = '---\ntitle: ' + category + '\nweight: 50\n---\n\n'
    elif category == '트윗':
        meta = '---\ntitle: ' + category + '\nweight: 60\n---\n\n'
    elif category == '가상화폐':
        meta = '---\ntitle: ' + category + '\nweight: 70\n---\n\n'
    # md 파일에 추가
    with open(md, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(meta.rstrip('\r\n') + '\n' + content + '\n' + foot_padding)


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
        else:
            site_name = ('&nbsp;' * 7) + dataframe.iloc[i]['site'] + ('&nbsp;' * 7)
        # 정보 표시줄(사이트명, 날짜_시간) 생성, 날짜_시간은 분까지만 표시되게 함
        con_info = "<td><span style='background-color:" + site_col[dataframe.iloc[i]['site']] + "'><font color='white'>" + \
        site_name + "</font></span>&nbsp;&nbsp;&nbsp;" + dataframe.iloc[i]['date_time'][:-3] + '&nbsp;&nbsp;' + \
        '<b><font color="CornflowerBlue">' + dataframe.iloc[i]['view_num'] + '</font>&nbsp;&nbsp;<font color="orange">[' + \
        dataframe.iloc[i]['reply_num'] + "]</font></b></td></tr>\n"
        # 정보 줄에 html 코드 삽입
        content += html_info + con_info

    content += "</table>\n\n"

    # footer(더보기) 추가하기 위한 html코드
    html_code_page = '/"><center><b><font color="darkblue" size=4><i class="icon icon-download"></i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;더 보기&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i class="icon icon-download"></i></font></b></center></a>'
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


# 함수: 검색 url에 키워드 추가
def add_keyword(subject=None, site=None, word=None, eto_link=None):
    # 사이트별 추가할 url 패딩 캐릭터
    clien_pad_1 = 'https://www.clien.net/service/search?q='
    clien_pad_2 = '&sort=recency&boardCd=park&boardName=%EB%AA%A8%EB%91%90%EC%9D%98%EA%B3%B5%EC%9B%90'
    ddan_pad_1 = 'http://www.ddanzi.com/index.php?mid=free&act=IS&search_target=all&is_keyword='
    ddan_pad_2 =  '&m=0'
    eto_pad_1 = 'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx='
    eto_pad_2 = '&x=0&y=0'
    mlb_pad_1 = 'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query='
    mlb_pad_2 = '&x=0&y=0'
    ruli_pad = 'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key='
    humor_pad = 'http://m.humoruniv.com/board/list.html?table=pdswait&st=subject&searchday=1year&sk='
    ppom_pad = 'http://m.ppomppu.co.kr/new/bbs_list.php?id=freeboard&category=&search_type=sub_memo&keyword='
    Ou_pad = 'http://m.todayhumor.co.kr/list.php?kind=search&table=total&search_table_name=total&keyfield=subject&keyword='
    inven_pad = 'http://m.inven.co.kr/board/powerbbs.php?come_idx=2097&stype=content&svalue='
    cook_pad = 'http://www.82cook.com/entiz/enti.php?bn=15&searchType=search&search1=1&search1=2&keys='
    
    b_word = word.encode('utf-8')
    import re
    b_word = str(b_word).replace('\\x', '%').replace("\'", '').upper()
    b_word = re.sub(r'^B', '', b_word)
    print(b_word)

    import json
    # 저장된 url json 파일 열기
    with open('links/' + subject + '.json','r') as f:
        url = json.load(f)
    
    # 특정 사이트의 url만 수정 케이스
    if site is not None:
        if site in ['ruli', 'ppom', 'Ou', 'inven', '82cook']:
            # 사이트명에서 숫자 제거한 pad를 붙임(82cook 때문)
            pad = locals()[re.search(r'[^0-9]+', site).group() + '_pad']
            try:
                url[site][word] = pad + b_word
            except KeyError:
                url[site] = {word: pad + b_word}
        elif site == 'slr':
            try:
                url[site][word] = b_word
            except KeyError:
                url[site] = {word: b_word}
        elif site in ['clien', 'mlb', 'ddan']:
            pad_1 = locals()[site + '_pad_1']
            pad_2 = locals()[site + '_pad_2']
            try:
                url[site][word] = pad_1 + b_word + pad_2
            except KeyError:
                url[site] = {word: pad_1 + b_word + pad_2}
        elif site == 'eto':
            try:
                url[site][word] = eto_link
            except KeyError:
                url[site] = {word:eto_link}
    # 전체 사이트에 키워드 검색 url 추가하기
    else:
        for site in ['clien', 'ddan', 'ruli', 'mlb', 'Ou', 'ppom', 'slr', '82cook', 'inven']:
            if site in ['ruli', 'ppom', 'Ou', 'inven', '82cook']:
                pad = locals()[re.search(r'[^0-9]+', site).group() + '_pad']
                try:
                    url[site][word] = pad + b_word
                except KeyError:
                    url[site] = {word: pad + b_word}
            elif site == 'slr':
                try:
                    url[site][word] = b_word
                except KeyError:
                    url[site] = {word: b_word}
            elif site in ['clien', 'mlb', 'ddan']:
                pad_1 = locals()[site + '_pad_1']
                pad_2 = locals()[site + '_pad_2']
                try:
                    url[site][word] = pad_1 + b_word + pad_2
                except KeyError:
                    url[site] = {word: pad_1 + b_word + pad_2}
        # 이토렌트는 별도로 추가
        try:
            url['eto'][word] = ''
        except KeyError:
            url['eto'] = {word:''}
        # url['HuU'][word] = humor_pad + b_word
        
    # url json 파일 저장하기
    with open('links/' + subject + '.json', 'w') as f:
        json.dump(url, f)
    
    print(url)


# 함수: 머신러닝 학습용 샘플데이터 저장
def export_sample(df, object):
    from xlsxwriter.utility import xl_rowcol_to_cell
    writer = pd.ExcelWriter('sample_data/sample_' + object + '_tmp.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='to')


# 제목에 트윗이 표시된 것만 추출하는 함수
def tweet_name_filter(dataframe):
    cond_1 = dataframe['title'].str.contains('트윗$')
    cond_2 = dataframe['title'].str.contains('트윗\.')
    cond_3 = dataframe['title'].str.contains('트위터$')
    cond_4 = dataframe['title'].str.contains('트위터\.')
    dataframe = dataframe[cond_1 | cond_2 | cond_3 | cond_4]
    dataframe['result'] = 'Y'
    return(dataframe)
