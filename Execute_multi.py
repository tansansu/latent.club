# 2018.07.21

# 업데이트 클래스 임포트
from Update_multi import Updater
from multiprocessing import Process
from datetime import datetime
import json


def multi_operation(roller_class, input_sites):
    procs = []
    for index, number in enumerate(input_sites):
        proc = Process(target=roller_class.run, args=(number,))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()


class Roller(Updater):
    def __init__(self):
        Updater.__init__(self)
        

if __name__ == '__main__':
    # 코드 동작 시간 측정용
    start_time = datetime.now().replace(microsecond=0)
    log_tmp = 'Start_time: ' + str(datetime.now().replace(microsecond=0))
    print(log_tmp)
    # Check Status file
    with open('./status.conf', 'r') as f:
        opt = json.load(f)

    if opt['status'] == 1:
        print('Running!')
    else:
        # 업데이트 클래스 초기화
        roller = Roller()
        # print(roller.subjects)
        # roller.log += log_tmp + '\n'
        roller.start_time = start_time
        # 스크랩 대상 주제 설정
        complete_subj_idx = roller.subjects.index(opt['subject'])
        subjects_cnt = len(roller.subjects)
        print('Current Index: %d/%d' % (complete_subj_idx, subjects_cnt))
        if complete_subj_idx == subjects_cnt-1:
            subject = roller.subjects[0]
        else:
            subject = roller.subjects[complete_subj_idx+1]
        # print(subject_key)
        
        # 실행중 상태 기록
        opt['status'] = 1
        opt['subject'] = subject
        with open('./status.conf', 'w') as f:
            json.dump(opt, f)

        # 검색 url 불러오기
        with open('./links/' + roller.subject_dict[subject] + '.json', 'r') as f:
            url = json.load(f)

        # 업데이트 실행(하나의 카테고리에 대해서 각 사이트를 여러개의 프로세스로 실행)
        roller.subject = subject  # 카테고리 설정(랜덤한 3개를 설정함)
        # 카테고리와 시작 시간 기록
        roller.log = '[ %s ]\nStart_time: %s\n' % (subject, roller.start_time)
        with open('./log/scrap.log', 'a') as f:
            f.write(roller.log)
        # site는 11개를 3개씩 순차적으로 실행
        multi_operation(roller, roller.sites[:3])
        print('Step1 completed')
        multi_operation(roller, roller.sites[3:6])
        print('Step2 completed')
        multi_operation(roller, roller.sites[6:9])
        print('Step3 completed')
        multi_operation(roller, roller.sites[9:])
        print('Step4 completed')

        roller.end_time = datetime.now().replace(microsecond=0)
        # log에 동작 시간 추가
        message = '업데이트 동작 시간: %s\n' % str(roller.end_time - roller.start_time)
        print(message)
        with open('./log/scrap.log', 'a') as f:
            f.write(message)

        # 주제의 게시글이 전부 수집될 때만 전송
        if complete_subj_idx == subjects_cnt-1:
            # 과거 log 불러오기
            with open('./log/scrap.log', 'r') as f:
                log_tmp = ''.join(f.readlines())
            # 텔레그램으로 발송
            roller.log2telegram(log_tmp)
            # 로그파일 초기화
            with open('./log/scrap.log', 'w') as f:
                f.write('')
                
        # 작업 종료 상태 기록
        opt['status'] = 0
        with open('./status.conf', 'w') as f:
            json.dump(opt, f)

