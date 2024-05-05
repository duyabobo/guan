#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.activity import ActivityModel
from model.address import AddressModel
from model.user import UserModel
from service import BaseService
from util.class_helper import lazy_property
from util.const.qiniu_img import CDN_QINIU_ADDRESS_URL, CDN_QINIU_ADDRESS_IMG, CDN_QINIU_TIME_IMG


class GuanguanService(BaseService):

    def __init__(self, redis, passportId):
        self.redis = redis
        self.passportId = passportId
        super(GuanguanService, self).__init__(redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.passportId)

    def match(self, activity, userMap):
        """筛选掉不符合期望的，筛选掉已完成匹配但是没有当前用户参与的"""
        # todo 资料/预期对比排除
        inv_pid = activity.girl_passport_id
        ac_pid = activity.boy_passport_id
        if inv_pid and ac_pid and self.passportId not in [inv_pid, ac_pid]:
            return False

        return True

    def getUserMap(self, passportIds):
        return []

    def getActivityList(self, addressIds):
        """
        1. 筛选掉已经完成的，已经过期的
        2. 筛选掉不符合邀请人期望的
        """
        if not addressIds:
            return []

        _activityList = ActivityModel.listByAddressIds(addressIds)  # 筛选掉已经已经过期的
        passportIds = []  # todo 所有涉及到的passportId列表，包括自己的passportid，以及活动里已参与的passportid
        userMap = self.getUserMap(passportIds)
        activityList = []  # 筛选掉不符合邀请人期望的，以及已完成的（但是保留自己参与的）
        for a in _activityList:
            if self.match(a, userMap):
                activityList.append(a)

        return activityList

    def getAddressMap(self, longitude, latitude):
        addressList = AddressModel.listByLongitudeLatitude(longitude, latitude)  # 根据地理位置查出activity
        return {
            a.id: a for a in addressList
        }

    def getState(self, activity):
        girl_pid = activity.girl_passport_id
        boy_pid = activity.boy_passport_id
        if not girl_pid and not boy_pid:
            return "报名"
        elif self.passportId in [girl_pid, boy_pid]:
            return "报名"
        else:
            return "报名"

    def reSortActivityList(self, activityList, ongoingActivity):
        for a in activityList:
            if a.id == ongoingActivity.id:
                activityList.remove(a)
                break
        activityList.insert(0, ongoingActivity)

    def fillAddressMap(self, addressMap, addressId):
        if addressId in addressMap:
            return
        address = AddressModel.getById(addressId)
        addressMap[address.id] = address

    def getGuanguanList(self, longitude, latitude):
        """优先展示有邀请人的，其次没有邀请人的，不分页直接返回最多20个，todo 如果超过20个满足，需要有一种轮训机制展示"""
        addressMap = self.getAddressMap(longitude, latitude)
        activityList = self.getActivityList(addressMap.keys())  # todo next 自己参与过的，后期还有流程环节要做

        ongoingActivity = ActivityModel.getOngoingActivity(self.passportId)
        if ongoingActivity:  # 进行中的永远在第一位
            self.reSortActivityList(activityList, ongoingActivity)
            self.fillAddressMap(addressMap, ongoingActivity.address_id)

        guanguanList = []
        for activity in activityList[:20]:
            address = addressMap[activity.address_id]
            guanguanList.append(
                {
                    "id": activity.id,
                    "time": activity.startTimeStr,
                    # "boyImg": activity.boyImg,
                    # "girlImg": activity.girlImg,
                    "state": self.getState(activity),
                    "img": CDN_QINIU_ADDRESS_URL + address.img_obj_name,
                    "addressImg": CDN_QINIU_ADDRESS_IMG,
                    "timeImg": CDN_QINIU_TIME_IMG,
                    "address": address.name,
                }
            )

        return guanguanList
