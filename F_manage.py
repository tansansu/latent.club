# 2018.01.07

#import pdb
import pickle
import json
import pandas as pd
import sqlite3


# 함수: 수집한 게시글이 db에 저장된 게시글과 중복인지 확인
def compare_article(category, site, dataframe, connection):
    # 중복 게시글 제거
    try:
        dataframe.drop_duplicates('article_id', inplace=True)
        dataframe.drop_duplicates('title', inplace=True)
    except:
        pass
    dataframe['article_id'] = dataframe['article_id'].astype('int')
    # db에서 게시물 추출
    
    query = 'select article_id from ' + category + ' where site = "' + site + \
    '" order by date_time desc limit 2000;'
    temp = pd.read_sql(query, connection)
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
    conn = sqlite3.connect('./db/board.db')
    new_d = compare_article(subject, site, dataframe, conn)
    # 수집한 new 게시글
    article_count = new_d.shape[0]
    if article_count >= 1:
        ## 신규 자료는 DB에 저장
        new_d.to_sql(subject, conn, if_exists='append', index=False)
    
    conn.close()
    # 수집한 new 게시글 개수 리턴
    return(article_count)


# 함수: 머신러닝 학습용 샘플데이터 저장
def export_sample(df, object):
    from xlsxwriter.utility import xl_rowcol_to_cell
    writer = pd.ExcelWriter('sample_data/sample_' + object + '_tmp.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='to')


# 중복 데이터 정리 함수
def clean_dup(path_db):
    # 정리할 테이블
    tables = ['estate', 'stock', 'economy', 'tabloid', 'coin', 'tweet']
    conn = sqlite3.connect(path_db)
    for table in tables:
        df = pd.read_sql('select * from %s;' % table, conn)
        before_lines = df.shape[0]
        df.drop_duplicates(['site', 'article_id'], inplace=True)
        after_lines = df.shape[0]
        df.to_sql(table, conn, if_exists='replace', index=False)
        # 결과 출력
        print('%s | before: %d  after: %d' % (table, before_lines, after_lines))
    conn.close()


# 모델 prediction 업데이트 함수
def update_article_result(path_db):
    # 정리할 테이블
    tables = ['estate', 'stock', 'economy', 'tabloid', 'coin']
    conn = sqlite3.connect(path_db)
    # 모델 파일 로딩 패키지
    import F_Classifier
    for table in tables:
        print(table)
        df = pd.read_sql('select * from %s;' % table, conn)
        before_y = sum(df.result == 'Y')
        df = F_Classifier.predict_Y(df, table)
        after_y = sum(df.result == 'Y')
        df.to_sql(table, conn, if_exists='replace', index=False)
        # 결과 출력
        print('%s | before: %d  after: %d' % (table, before_y, after_y))
    conn.close()


'''
firebase 이용 함수(삭제)
def firebase():
    with open('db/firebase.config', 'r') as f:
        config = json.load(f)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    return(db)
'''
