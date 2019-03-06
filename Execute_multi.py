# 2018.07.21

# 업데이트 클래스 임포트
from Update_multi import Updater
from F_Classifier import Classifier
from datetime import datetime
import json
import time
import os
import pandas as pd


class Roller(Updater):
    def __init__(self):
        Updater.__init__(self)
        

if __name__ == '__main__':
    # 코드 동작 시간 측정용
    start_time = datetime.now().replace(microsecond=0)
    log_tmp = 'Start_time: ' + str(start_time)
    print("=====%s" % log_tmp)
    # Check Status file
    with open('./status.conf', 'r') as f:
        opt = json.load(f)

    if opt['status'] == 1:
        old_time = datetime.strptime(opt['date_time'], '%Y-%m-%d %H:%M:%S')
        time_delta = start_time - old_time
        print("=====time delta: %f" % (time_delta.seconds / 3600))
        if time_delta.seconds / 3600 >= 5:
            opt['status'] = 0
        print('=====Running!')
    else:
        # 업데이트 클래스 초기화
        roller = Roller()
        # print(roller.subjects)
        # roller.log += log_tmp + '\n'
        roller.start_time = start_time
        # 스크랩 대상 주제 설정
        complete_subj_idx = roller.subjects.index(opt['subject'])
        subjects_cnt = len(roller.subjects)
        print('=====Current Index: %d/%d' % (complete_subj_idx, subjects_cnt))
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

        roller.subject = subject  # 카테고리 설정
        if roller.subject not in ['트윗', '감동', '근황']:
            roller.classifier = Classifier(roller.subject_dict[roller.subject])
        # 카테고리와 시작 시간 기록
        roller.log = '[ %s ]\nStart_time: %s\n' % (subject, roller.start_time)
        with open('./log/scrap.log', 'a') as f:
            f.write(roller.log)

        # 업데이트 실행(하나의 카테고리에 대해서 각 사이트를 여러개의 프로세스로 실행)
        roller.multi_operation(roller.sites)

        # 사이트별로 스크랩이 데이터프레임을 읽은 후 주제 적합성 판정(트윗 제외)
        result = pd.DataFrame()
        for fname in os.listdir('./temp'):
            df_tmp = pd.read_pickle('./temp/' + fname)
            site_name = roller.site_dict_rev[fname.replace('.pkl', '')]
            article_count = df_tmp.shape[0]
            # 프린트 메시지
            tmp_log = '-%s: %d개 수집' % (site_name, article_count)
            print(tmp_log)
            tmp_log += '\n'  # 텔레그램 메세징 용으로
            result = result.append(df_tmp)
            # 게시물 수집 log 텔레그램으로 전송하기 위해 파일로 저장
            with open('./log/scrap.log', 'a') as f:
                f.write(tmp_log)
        # 분류 및 DB 저장
        roller.predict_store(result)

        # md 파일 생성
        roller.execute_md(size=300)

        roller.end_time = datetime.now().replace(microsecond=0)
        # log에 동작 시간 추가
        message = '업데이트 동작 시간: %s\n' % str(roller.end_time - roller.start_time)
        print("=====%s" % message)
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
        opt['date_time'] = str(roller.end_time)
        with open('./status.conf', 'w') as f:
            json.dump(opt, f)

        # hugo 페이지 생성 및 Git Push
        print('=====Make pages with hugo!')
        roller.run_hugo('/home/revlon/Codes/Web/hugo_latent-info')
        time.sleep(8)
        roller.git_commit('/home/revlon/Codes/Web/latent-info.github.io')
