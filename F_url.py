'''
함수: 검색 url에 키워드 추가
'''

# 2017.12.31

def add_keyword(subject=None, site=None, word=None, eto_link=None):
    # 사이트별 추가할 url 패딩 캐릭터
    clien_pad_1 = 'https://www.clien.net/service/search?q='
    clien_pad_2 = '&sort=recency&boardCd=park&boardName=%EB%AA%A8%EB%91%90%EC%9D%98%EA%B3%B5%EC%9B%90'
    eto_pad_1 = 'http://etorrent.co.kr/plugin/mobile/board.php?bo_table=eboard&sca=&sfl=wr_subject%7C%7Cwr_content&stx='
    eto_pad_2 = '&x=0&y=0'
    mlb_pad_1 = 'http://mlbpark.donga.com/mp/b.php?select=sct&m=search&b=bullpen&select=sct&query='
    mlb_pad_2 = '&x=0&y=0'
    ddan_pad = 'http://www.ddanzi.com/?_filter=search&act=&vid=&mid=free&category=&search_target=title_content&search_keyword='
    ruli_pad = 'http://m.ruliweb.com/community/board/300148?search_type=subject_content&search_key='
    humor_pad = 'http://m.humoruniv.com/board/list.html?table=pdswait&st=subject&searchday=1year&sk='
    ppom_pad = 'http://m.ppomppu.co.kr/new/bbs_list.php?id=freeboard&category=&search_type=sub_memo&keyword='
    Ou_pad = 'http://m.todayhumor.co.kr/list.php?kind=search&table=total&search_table_name=total&keyfield=subject&keyword='
    inven_pad = 'http://m.inven.co.kr/board/powerbbs.php?come_idx=2097&stype=content&svalue='
    cook_pad = 'http://www.82cook.com/entiz/enti.php?bn=15&searchType=search&search1=1&search1=2&keys='
    
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

    import json
    # 저장된 url json 파일 열기
    with open('links/' + subject + '.json','r') as f:
        url = json.load(f)
    
    import re
    # 특정 사이트의 url만 수정 케이스
    if site != None:
        if site in ['ddan', 'ruli', 'ppom', 'Ou', 'inven', '82cook']:
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
        elif site in ['clien', 'mlb']:
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
            if site in ['ddan', 'ruli', 'ppom', 'Ou', 'inven', '82cook']:
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
            elif site in ['clien', 'mlb']:
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
