# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2023/4/8 21:59
#  File: getSchoolData.py
#  Software: PyCharm
import time

import requests

from model.region import RegionModel
from model.school import SchoolModel
from util.const.base import ALL_STR

URL = "https://daxue.hao86.com/searchc/"


def getByPage(page):
    url = "%s?page=%s" % (URL, page)
    resp = requests.get(url)
    schools = resp.json()['data']['data']
    for s in schools:
        cityName = s['city_name']
        townName = s['town_name']
        levelName = s['level_name']
        name = s['name']  # 学校名称
        logo = s['logo']  # 学校logo
        natureName = s['nature_name']  # 民办还是公办性质
        schoolTypeName = s['school_type_name']  # 专科还是本科
        if cityName in [u'澳门半岛', u'离岛']:
            cityName = u'香港特别行政区'
        if townName in [u'全市', u'']:
            townName = ALL_STR
        regionId = RegionModel.getRegionIdByArea(townName)
        if not regionId:
            regionId = RegionModel.getRegionIdByCity(cityName)
        if not regionId:
            print "city and area not found: school=%s city=%s, area=%s" % (name, cityName, townName)
            continue
        ret = SchoolModel.addOne(regionId, name, logo, levelName, natureName, schoolTypeName)
        print 'success ret.id=%s' % ret.id


if __name__ == '__main__':
    for page in range(190):
        getByPage(page)
        time.sleep(1)
