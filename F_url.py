'''
함수: 검색 url에 키워드 추가
'''

import json

# 2018.05.05
# 링크 json에 새로운 사이트 추가
def add_site(site, subject=None):   
    if subject:
        # 저장된 url json 파일 열기
        with open('links/' + subject + '.json','r') as f:
            url = json.load(f)
        # site 추가
        url[site] = ''
        # url json 파일 저장하기
        with open('links/' + subject + '.json', 'w') as f:
            json.dump(url, f)
        print(url[site])
    else:
        subjects = ['estate', 'stock', 'economy', 'tabloid', 'coin', 'tweet']
        for sub in subjects:
            with open('links/' + sub + '.json','r') as f:
                url = json.load(f)
            # site 추가
            url[site] = ''
            # url json 파일 저장하기
            with open('links/' + sub + '.json', 'w') as f:
                json.dump(url, f)
            print(url[site])
    

# 링크 json에 새로운 사이트 삭제
def del_site(site, subject=None):   
    if subject:
        # 저장된 url json 파일 열기
        with open('links/' + subject + '.json','r') as f:
            url = json.load(f)
        # site 제거
        del(url[site])
        # url json 파일 저장하기
        with open('links/' + subject + '.json', 'w') as f:
            json.dump(url, f)
    else:
        subjects = ['estate', 'stock', 'economy', 'tabloid', 'coin', 'tweet']
        for sub in subjects:
            with open('links/' + sub + '.json','r') as f:
                url = json.load(f)
            # site 제거
            del(url[site])
            # url json 파일 저장하기
            with open('links/' + sub + '.json', 'w') as f:
                json.dump(url, f)


# 함수 실행 예: add_keyword(subject='tweet', site='eto', word='abcd', eto_link='')
def add_keyword(subject=None, site=None, word=None, eto_link=None):
    # 사이트별 추가할 url 패딩 캐릭터
    clien_pad = 'https://www.clien.net/service/search?q={0}&sort=recency&boardCd=park&boardName=%EB%AA%A8%EB%91%90%EC%9D%98%EA%B3%B5%EC%9B%90'
    eto_pad = 'http://www.etoland.co.kr/plugin/mobile/board.php?bo_table=etoboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx={0}'
    mlb_pad = 'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query={0}&x=0&y=0'
    ddan_pad = 'http://www.ddanzi.com/?_filter=search&act=&vid=&mid=free&category=&search_target=title_content&search_keyword={0}'
    ruli_pad = 'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key={0}'
    humor_pad = 'http://m.humoruniv.com/board/list.html?table=pdswait&st=subject&searchday=1year&sk={0}'
    ppom_pad = 'http://m.ppomppu.co.kr/new/bbs_list.php?id=freeboard&category=&search_type=sub_memo&keyword={0}'
    Ou_pad = 'http://m.todayhumor.co.kr/list.php?kind=search&table=total&search_table_name=total&keyfield=subject&keyword={0}'
    inven_pad = 'http://m.inven.co.kr/board/powerbbs.php?come_idx=2097&stype=content&svalue={0}'
    cook_pad = 'http://www.82cook.com/entiz/enti.php?bn=15&searchType=search&search1=1&search1=2&keys={0}'
    dvd_pad = 'https://dvdprime.com/g2/bbs/board.php?bo_table=comm&sca=&scrap_mode=&sfl=wr_subject%7C%7Cwr_content&sop=and&stx={0}'
    instiz_pad = 'https://www.instiz.net/bbs/list.php?starttime=&endtime=&k={0}&id=pt'
    
    '''
    b_word = word.encode('utf-8')
    import re
    b_word = str(b_word).replace('\\x', '%').replace("\'", '').upper()
    b_word = re.sub(r'^B', '', b_word)
    '''
    # 입력된 단어의 urlencoding
    from urllib.parse import quote_plus
    b_word = quote_plus(word)
    print(b_word)

    # 저장된 url json 파일 열기
    with open('links/' + subject + '.json','r') as f:
        url = json.load(f)
    
    import re
    
    # url dictionary에 url에 추가하는 함수
    def put_link(url_dict, site, word, url_string):
        try:
            url_dict[site][word] = url_string
        except KeyError:
            url_dict[site] = {word:url_string}
        except TypeError:
            url_dict[site] = {word:url_string}
        return(url_dict)

    # 특정 사이트의 url만 수정 케이스
    if site:
        if site == 'eto':
            eto_link = eto_pad.format(eto_link)
            url = put_link(url, site, word, eto_link)
        elif site == 'slr':
            url = put_link(url, site, word, b_word)
        else:
            pad = locals()[re.search(r'[^0-9]+', site).group() + '_pad']
            url = put_link(url, site, word, pad.format(b_word))
    # 전체 사이트에 키워드 검색 url 추가하기
    else:
        sites = ['clien', 'ddan', 'ruli', 'mlb', 'Ou', 'ppom', '82cook', \
        'inven', 'dvd', 'instiz']
        for site in sites:  
            pad = locals()[re.search(r'[^0-9]+', site).group() + '_pad']
            url = put_link(url, site, word, pad.format(b_word))
        # SLR은 키워드만 추가
        url = put_link(url, 'slr', word, b_word)
        # 이토렌트는 None이면 공백으로 추가
        if not(eto_link):
            url = put_link(url, 'eto', word, '')
        else:
            url = put_link(url, 'eto', word, eto_pad.format(eto_link))
        
        
    # url json 파일 저장하기
    with open('links/' + subject + '.json', 'w') as f:
        json.dump(url, f)
    
    print(url)


# etoland 링크 변경
def change_url(target='eto'):
    import re
    # url과 변경할 주제
    subjects = ['estate', 'stock', 'economy', 'tabloid', 'coin', 'tweet']
    eto_pad = 'http://www.etoland.co.kr/plugin/mobile/board.php?bo_table=etoboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx=%BA%CE%B5%BF%BB%EA{0}'
    # 키워드 추출
    for subject in subjects:
        # 저장된 url json 파일 열기
        with open('links/' + subject + '.json', 'r') as f:
            url = json.load(f)
        target_url = url[target]
        for k in target_url.keys():
            word = target_url[k]
            b_word = re.search(r'=%.+&', test).group().replace('=', '').replace('&x0&', '')
            target_url[k] = eto_pad.format(b_word)
        url[target] = target_url
        print(url[target])
        # URL 파일 저장
        with open('links/' + subject + '.json', 'w') as f:
            json.dump(url, f)
        
    