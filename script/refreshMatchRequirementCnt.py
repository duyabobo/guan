#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 刷新符合你期望的人数。这个脚本暂时用不着。
# 1，更新期望后（期望信息完备的前提下），立刻计算一次。对user表建立索引。每天允许更新3次期望。
# 2，定时全量刷新
import sys
print sys.path
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))

import time
from model.user import UserModel

FIRST_PASSPORT_ID = 0
LIMIT = 500
MAX_RUNTIME_SECONDS = 600  # 超过10分钟，就告警这个脚本需要分布式跑了


def refreshLimitUser(lastPassportId, limit):
    users = UserModel.getLimitUserList(lastPassportId, limit)
    passportId = 0
    for u in users:
        passportId = u.passport_id
        UserModel.getMatchCnt(passportId=passportId, forceRefreshCache=True)
    return passportId


if __name__ == '__main__':
    fromTime = time.time()
    lastPassportId = refreshLimitUser(FIRST_PASSPORT_ID, LIMIT)
    while lastPassportId:
        lastPassportId = refreshLimitUser(lastPassportId, LIMIT)
    timeCost = time.time() - fromTime
    if timeCost > MAX_RUNTIME_SECONDS:
        pass  # 报警一下，需要分布式跑脚本了
