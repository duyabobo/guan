#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 获取大学专业数据
import sys

print sys.path
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))

from util.const.base import ALL_STR
import requests
from bs4 import BeautifulSoup

from model.region import RegionModel
from util.ctx import getDbSession

url = "https://www.mca.gov.cn/article/sj/xzqh/2020/2020/202003061536.html"


def getPageData():
    ret = requests.get(url)
    soup = BeautifulSoup(ret.content, 'html.parser')
    tr_list = soup.body.div.table.find_all('tr')
    code_map_province = {}
    code_map_city = {}
    code_map_area = {}

    for tr in tr_list:
        data = []
        for td in tr.find_all('td'):
            data.append(td.text)
        if len(data) < 2:
            print data
            continue
        code = data[1]
        value = data[2].strip()
        if not code.isdigit():
            print data
            continue
        code = int(code)
        if code % 10000 == 0:  # 省份
            code_map_province[code / 10000] = value
            code_map_city[code / 100] = ALL_STR
            code_map_area[code] = ALL_STR
        elif code % 100 == 0:  # 市
            code_map_city[code / 100] = value
            code_map_area[code] = ALL_STR
        else:  # 区
            code_map_area[code] = value

    for code, area in sorted(code_map_area.items(), key=lambda x: x[0]):
        province = code_map_province[code/10000]
        if province in [u'北京市', u'天津市', u'上海市', u'重庆市']:
            city = province
        elif code / 100 % 100 == 90:  # 省直辖县级市
            city = u'省直辖县级市'
        else:
            city = code_map_city[code/100]
        RegionModel.getIdByRegion(province, city, area)

    getDbSession().commit()


if __name__ == '__main__':
    getPageData()
