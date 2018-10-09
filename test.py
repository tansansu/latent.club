from Update_multi import Updater
from F_Classifier import Classifier
from datetime import datetime
import json
import os
import pandas as pd


class Roller(Updater):
    def __init__(self):
        Updater.__init__(self)

start_time = datetime.now().replace(microsecond=0)
log_tmp = 'Start_time: ' + str(datetime.now().replace(microsecond=0))

with open('./status.conf', 'r') as f:
    opt = json.load(f)

roller = Roller()

roller.start_time = start_time
# 스크랩 대상 주제 설정
complete_subj_idx = roller.subjects.index(opt['subject'])
subjects_cnt = len(roller.subjects)

if complete_subj_idx == subjects_cnt - 1:
    subject = roller.subjects[0]
else:
    subject = roller.subjects[complete_subj_idx + 1]

with open('./links/' + roller.subject_dict[subject] + '.json', 'r') as f:
    url = json.load(f)

roller.subject = subject  # 카테고리 설정
roller.classifier = Classifier(roller.subject_dict[subject])

roller.multi_operation(roller.sites[1:2])