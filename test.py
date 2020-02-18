from Update_multi import Updater
#from F_Classifier import Classifier
from datetime import datetime
import json
import os
import pandas as pd
import F_common


class Roller(Updater):
    def __init__(self):
        Updater.__init__(self)


def scrap_test(subject: str, site: str, keyword: str=None):
    start_time = datetime.now().replace(microsecond=0)
    log_tmp = 'Start_time: ' + str(datetime.now().replace(microsecond=0))
    
    roller = Roller()
    roller.start_time = start_time

    # 스크랩 대상 주제 설정
    complete_subj_idx = roller.subjects.index(subject)

    roller.subject = subject  # 카테고리 설정
    with open('links/%s.json' % roller.subject_dict[subject], 'r') as f:
        url = json.load(f)
    result = F_common.scrapper(site, url, roller.subject_dict[subject], roller.site_dict, keyword, True)

