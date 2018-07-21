# 2018.07.21

# 업데이트 클래스 임포트
from Update import Updater
import sys


class FractUp(Updater):
    def __init__(self, subject, site):
        Updater.__init__(self)
        self.subjects = [subject]
        self.sites = [site]
        

if __name__ == '__main__':
    # 주제와 사이트의 인자로 업데이터 클래스 초기화
    updater = FractUp(sys.argv[1], sys.argv[2])
    # 업데이트 실행
    updater.run()