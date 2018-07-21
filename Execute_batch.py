# 2018.07.21

# 업데이트 클래스 임포트
from Update import Updater
import sys


class Roller(Updater):
    def __init__(self):
        Updater.__init__(self)
        
        

if __name__ == '__main__':
    # Check Status file
    with open('./status.conf', 'r') as f:
        opt = json.load(f)

    if opt['status'] == 1:
        print('Running!')
    else:
        complete_subj_idx = self.subjects.index(opt['subject'])
        if complete_subj_idx == len(self.subjects)-1:
            subject = self.subjects[0]
        else:
            subject = self.subjects[complete_subj_idx+1]
        #print(subject_key)
        
        # 실행중 상태 기록
        opt['status'] = 1
        opt['subject'] = subject
        with open('./status.conf', 'w') as f:
            json.dump(opt, f)

        # log 메세지 생성
        log = '[ %s ]\n' % subject_key
        # 코드 동작 시간 측정용
        start_time = datetime.now().replace(microsecond=0)
        # 로깅
        log += 'Start_time: ' + str(start_time) + '\n'
        print(log)

        # 검색 url 불러오기
        with open('./links/' + self.subjects[subject] + '.json','r') as f:
            url = json.load(f)

        # 업데이터 실행 전에 주제를 1개로 설정
        self.subjects = [subject]
        roller = Roller()
        # 업데이트 실행
        roller.run()

        # 게시물 수집 log 텔레그램으로 전송하기 위해 파일로 저장
        with open('./log/scrap.log', 'a') as f:
            f.write(log)
        ## 11개의 사이트가 전부 수집이 될 때만 전송
        if complete_subj_idx == len(subjects)-1:
            # 과거 log 불러오기
            with open('./log/scrap.log', 'r') as f:
                scrap_log = ''.join(f.readlines())
            # 텔레그램으로 발송
            roller.log2telegram(scrap_log)
            # 로그파일 초기화
            with open('./log/scrap.log', 'w') as f:
                f.write('')

        # 작업 종료 상태 기록
        opt['status'] = 0
        with open('./status.conf', 'w') as f:
            json.dump(opt, f)

