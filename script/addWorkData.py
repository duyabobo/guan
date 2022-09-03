#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 获取职业数据
from model.work import WorkModel
from util.ctx import getDbSession


def readData():
    fileName = '/Users/duyabo/work'
    workList = []
    with open(fileName, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            l = l.replace("GBM ", "GBM_")
            if 'GBM' in l:
                l = l.replace(' (GBM', '(')
                l = l.replace(')', ') ')
            if not l:
                continue
            elif not l[0].isdigit():
                continue
            elif l[0] == '1':
                continue
            elif l[0] == '8':
                continue
            elif l[0] == '7':
                continue
            elif len(l.split(' ')) > 2:
                l = l.replace('(工业) ', '(工业)')
                l = l.replace('(产品) ', '(产品)')
                l = l.replace('(苗) ', '(苗)')
                items = l.split(' ')
                if len(items) % 2 != 0:
                    continue
                for i in range(len(items)/2):
                    work = ' '.join(items[i*2: i*2+2])
                    workList.append(work)
            else:
                workList.append(l)

        print len(workList)

    work1Dict = {}
    work2Dict = {}
    work3Dict = {}
    for work in workList:
        dataList = work.split(' ')
        dataList[0] = dataList[0].split('(')[0]
        _data = dataList[0].split('-')
        if len(_data) == 1:
            work1Dict[dataList[0]] = dataList[1]
        elif len(_data) == 2:
            work2Dict[dataList[0]] = dataList[1]
        else:
            work3Dict[dataList[0]] = dataList[1]

    print len(work3Dict)
    for k3, v3 in work3Dict.items():
        for k2, v2 in work2Dict.items():
            if not k3.startswith(k2):
                continue
            for k1, v1 in work1Dict.items():
                if not k2.startswith(k1):
                    continue
                _k3 = ''.join(k3.split('-')[:3])
                WorkModel.getIdByData(v1, v2, v3, int(_k3))

    getDbSession().commit()


if __name__ == '__main__':
    readData()
