#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 每天跑一次脚本，对见面30天后，仍然没有选择意向的，按照自动发展看看处理
import sys
print sys.path
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))

from model.activity import ActivityModel


def closeActivities():
    ActivityModel.closeBoyActivities()
    ActivityModel.closeGirlActivities()


if __name__ == '__main__':
    closeActivities()
