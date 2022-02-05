#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.activity import ActivityModel
from model.address import AddressModel
from model.user import UserModel
from service import BaseService
from util import const
from util import util_time
from util.class_helper import lazy_property


class GuanguanService(BaseService):

    def __init__(self, dbSession, redis, passportId):
        self.dbSession = dbSession
        self.redis = redis
        self.passportId = passportId
        super(GuanguanService, self).__init__(dbSession, redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.dbSession, self.passportId)

    def match(self, activity):
        """筛选掉不符合期望的，筛选掉已完成匹配但是没有当前用户参与的"""
        # todo 资料/预期对比排除
        inv_pid = activity.invite_passport_id
        ac_pid = activity.accept_passport_id
        if inv_pid and ac_pid and self.passportId not in [inv_pid, ac_pid]:
            return False
        return True

    def getActivityList(self, addressIds):
        """
        1. 筛选掉已经完成的，已经过期的
        2. 筛选掉不符合邀请人期望的
        """
        if not addressIds:
            return []

        _activityList = ActivityModel.listByAddressIds(self.dbSession, addressIds)  # 筛选掉已经已经过期的
        activityList = []  # 筛选掉不符合邀请人期望的，以及已完成的（但是保留自己参与的）
        for a in _activityList:
            if self.match(a):
                activityList.append(a)

        return activityList

    def getAddressMap(self, longitude, latitude):
        addressList = AddressModel.listByLongitudeLatitude(self.dbSession, longitude, latitude)  # 根据地理位置查出activity
        return {
            a.id: a for a in addressList
        }

    def getState(self, activity):
        inv_pid = activity.invite_passport_id
        ac_pid = activity.accept_passport_id
        if inv_pid and ac_pid:
            return "匹配成功"
        elif inv_pid and self.passportId == inv_pid:
            return "我的邀请"
        elif inv_pid:
            return "邀请中"
        else:
            return "虚位以待"

    def getGuanguanList(self, longitude, latitude):
        """优先展示有邀请人的，其次没有邀请人的，不分页直接返回最多20个，todo 如果超过20个满足，需要有一种轮训机制展示"""
        addressMap = self.getAddressMap(longitude, latitude)
        activityList = self.getActivityList(addressMap.keys())

        guanguanList = []
        for activity in activityList:
            address = addressMap[activity.address_id]
            guanguanList.append(
                {
                    "id": activity.id,
                    "img": const.CDN_QINIU_URL + address.img,
                    "time": activity.startTimeStr,
                    "address": address.name,
                    "state": self.getState(activity),
                }
            )
        return guanguanList
