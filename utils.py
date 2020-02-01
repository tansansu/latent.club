import requests
import json


# 함수: 세션생성
def sess(referer: str):
    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    s = requests.Session()
    s.headers.update({'User-Agent': agent, 'Referer': referer})
    return s


# verbose printing
def print_log(verbose, category, obj):
    if verbose:
        print('===== catch %s: ' % category, obj)


# URL json 파일 불러오기
def get_url(subject: str) -> dict:
    with open('./links/%s.json' % subject, 'r') as f:
        url = json.load(f)
    return url


# URL json 파일 저장
def save_url(subject: str, url:dict):
    with open('./links/%s.json' % subject, 'w') as f:
        json.dump(url, f)
