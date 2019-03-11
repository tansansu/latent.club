# 2018.01.07

#import pdb
import pickle, json, sqlite3, sys
import pandas as pd
sys.path.insert(0, 'latent_info/')
sys.path.append('/home/revlon/Codes/Telegram_Bot/')
sys.path.append('/Users/tansansu/Google Drive/Python/Telegram_Bot/')
sys.path.append('/root/Codes/Telegram_Bot/')
from TelegramBot import TelegramBot


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


# 학습을 위한 데이터 생성 함수
def create_training_data(db_path):
    conn = sqlite3.connect(db_path)
    tables = ['estate', 'stock', 'economy', 'tabloid', 'coin', 'tweet', 'hot', 'touching']
    for table in tables:
        df_tmp = pd.read_sql('select * from %s order by date_time desc limit 500;' % table, conn)
        export_sample(df_tmp, table)
    conn.close()


# 함수: 머신러닝 학습용 샘플데이터 저장
def export_sample(df, object):
    from xlsxwriter.utility import xl_rowcol_to_cell
    writer = pd.ExcelWriter('sample_data/sample_' + object + '_tmp.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='to')


# 중복 데이터 정리 함수
def clean_dup(path_db):
    # 정리할 테이블
    tables = ['estate', 'stock', 'economy', 'tabloid', 'coin', 'tweet', 'hot', 'touching']
    conn = sqlite3.connect(path_db)
    for table in tables:
        df = pd.read_sql('select * from %s;' % table, conn)
        before_lines = df.shape[0]
        df.drop_duplicates(['site', 'article_id'], inplace=True)
        after_lines = df.shape[0]
        df.to_sql(table, conn, if_exists='replace', index=False)
        # 결과 출력
        print('%s | before: %d rows after: %d rows' % (table, before_lines, after_lines))
    conn.close()


# 모델 prediction 업데이트 함수
def update_article_result(path_db):
    # 정리할 테이블
    tables = ['estate', 'stock', 'economy', 'tabloid', 'coin']
    conn = sqlite3.connect(path_db)
    # 모델 파일 로딩 패키지
    import F_Classifier
    message = ''
    for table in tables:
        print(table)
        df = pd.read_sql('select * from %s;' % table, conn)
        before_y = sum(df.result == 'Y')
        df = F_Classifier.predict_Y(df, table)
        after_y = sum(df.result == 'Y')
        df.to_sql(table, conn, if_exists='replace', index=False)
        # 결과 출력
        message += '%s | before: %d  after: %d\n' % (table, before_y, after_y)
        #print(message)
    conn.close()
    TelegramBot().log_to_me(message)


# 주제별로 잘못된 키워드가 포함된 데이터 삭제 함수
def clean_keyword_error(path_db):
    # 정리할 테이블
    tables = ['tidings', 'tweet', 'estate', 'tabloid', 'economy', 'stock', 'touching', 'hot', 'coin']
    conn = sqlite3.connect(path_db)
    for table in tables:
        print(table)
        # 주제별 키워드 불러오기
        with open("./links/%s.json" % table, "r") as f:
            url = json.load(f)
        keywords = list(url['clien'].keys())
        # 테이블 전체 불러오기
        df = pd.read_sql('select * from %s;' % table, conn)
        print(df.shape)
        df_new = df[df['keyword'].isin(keywords)]
        print(df_new.shape)
        df_new.to_sql(table, conn, if_exists='replace', index=False)
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


if __name__ == '__main__':
    path_db = '/home/revlon/Codes/Web/latent_info/db/board.db'
    if sys.argv[1] == "dup":
        clean_dup(path_db)
    elif sys.argv[1] == "key":
        clean_keyword_error(path_db)
