import requests


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
