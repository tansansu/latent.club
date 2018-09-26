# 2018.07.21

# 업데이트 클래스 임포트
from Update import Updater
import sys
from datetime import datetime
import json


class Roller(Updater):
    def __init__(self):
        Updater.__init__(self)
        

if __name__ == '__main__':
    # 코드 동작 시간 측정용
    start_time = datetime.now().replace(microsecond=0)
    log_tmp = 'Start_time: ' + str(datetime.now().replace(microsecond=0))
    print(log_tmp)
    # Check Status file
    with open('./status_%s.conf' % sys.argv[1], 'r') as f:
        opt = json.load(f)

    if opt['status'] == 1:
        print('Running!')
    else:
        ## 업데이트 클래스 초기화
        roller = Roller()
        if sys.argv[1] == "one":
            roller.subjects = ['부동산', '경제', '가상화폐', '대란']
        elif sys.argv[1] == "two":
            roller.subjects = ['주식', '찌라시', '트윗', '감동']
        #print(roller.subjects)
        roller.log += log_tmp + '\n'
        roller.start_time = start_time
        ## 스크랩 대상 주제 설정
        complete_subj_idx = roller.subjects.index(opt['subject'])
        subjects_cnt = len(roller.subjects)
        print('Current Index: %d/%d' % (complete_subj_idx, subjects_cnt))
        if complete_subj_idx == subjects_cnt-1:
            subject = roller.subjects[0]
        else:
            subject = roller.subjects[complete_subj_idx+1]
        #print(subject_key)
        
        # 실행중 상태 기록
        opt['status'] = 1
        opt['subject'] = subject
        with open('./status_%s.conf' % sys.argv[1], 'w') as f:
            json.dump(opt, f)

        # 검색 url 불러오기
        with open('./links/' + roller.subject_dict[subject] + '.json','r') as f:
            url = json.load(f)

        # 업데이터 실행 전에 주제를 1개로 설정
        roller.subjects = [subject]
        # 업데이트 실행
        roller.run()

        # 게시물 수집 log 텔레그램으로 전송하기 위해 파일로 저장
        with open('./log/scrap_%s.log' % (sys.argv[1]), 'a') as f:
            f.write(roller.log)
        ## 주제의 게시글이 전부 수집될 때만 전송
        if complete_subj_idx == subjects_cnt-1:
            # 과거 log 불러오기
            with open('./log/scrap_%s.log' % (sys.argv[1]), 'r') as f:
                log_tmp = ''.join(f.readlines())
            # 텔레그램으로 발송
            roller.log2telegram(log_tmp)
            # 로그파일 초기화
            with open('./log/scrap_%s.log' % (sys.argv[1]), 'w') as f:
                f.write('')
                
        # 작업 종료 상태 기록
        opt['status'] = 0
        with open('./status_%s.conf' % sys.argv[1], 'w') as f:
            json.dump(opt, f)

