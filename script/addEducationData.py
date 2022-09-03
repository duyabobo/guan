#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 获取大学专业数据
import sys
print sys.path
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))
import json

import requests
from bs4 import BeautifulSoup

from model.education import EducationModel
from util.ctx import getDbSession

url = "https://www.dxsbb.com/news/8401.html"


def getPageData():
    ret = requests.get(url)
    soup = BeautifulSoup(ret.content, 'html.parser')
    tr_list = soup.tbody.find_all('tr')
    data_list = []
    for tr in tr_list:
        data = []
        for td in tr.find_all('td'):
            data.append(td.text)
        print json.dumps(data, ensure_ascii=False)
        data_list.append(data)
    for e in data_list[1:]:
        EducationModel.getIdByData(e[1], e[2], e[4], e[0])
    getDbSession().commit()


if __name__ == '__main__':
    getPageData()
