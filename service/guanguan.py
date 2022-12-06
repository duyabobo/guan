#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.activity import ActivityModel
from model.address import AddressModel
from model.user import UserModel
from ral.activity import getMatchedActivityIds
from ral.cache import checkCache
from service import BaseService
from service.common.guan_helper import GuanHelper
from util.class_helper import lazy_property
from util.const.match import MODEL_SEX_MALE_INDEX
from util.time_cost import timecost


class GuanguanService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        super(GuanguanService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    @timecost
    def getActivityIdsByLocation(self, longitude, latitude, hasLogin, limit):
        addressIds = self.getAddressIds(longitude=round(longitude, 2), latitude=round(latitude, 2), limit=limit*5)
        if not addressIds:
            addressIds = [0]
        activityIds = ActivityModel.listActivityIdsByAddressIds(addressIds, hasLogin, limit)
        return set([a.id for a in activityIds])

    @timecost
    def getLimitMatchedActivityList(self, activityIds, limit):
        return ActivityModel.listActivity(activityIds, limit, exceptPassportId=self.passportId)

    @timecost
    @checkCache("GuanguanService:{longitude}:{latitude}:{limit}")
    def getAddressIds(self, longitude, latitude, limit):
        addressList = AddressModel.listByLongitudeLatitude(longitude, latitude)  # 根据地理位置查
        addressIdMapDistance = {
            a.id: (a.longitude - longitude) ** 2 + (a.latitude - latitude) ** 2
            for a in addressList
        }
        return [k for k, v in sorted(addressIdMapDistance.items(), key=lambda x: x[1])][:limit]

    def getState(self, activity):
        girl_pid = activity.girl_passport_id
        boy_pid = activity.boy_passport_id
        if not girl_pid and not boy_pid:
            return "虚位以待"
        elif self.passportId in [girl_pid, boy_pid]:
            return "我的见面"
        else:
            return "见面邀请"

    @timecost
    def getAddressMapByIds(self, addressIds):
        if not addressIds:
            return {}
        addressList = AddressModel.listByIds(addressIds)
        return {a.id: a for a in addressList}

    @timecost
    def getMatchUserByIds(self, passportIds):
        if not passportIds:
            return {}
        users = UserModel.getByPassportIds(passportIds)
        return {u.passport_id: u for u in users}

    def getMatchPassportId(self, activity):
        if not self.userInfo:
            return activity.girl_passport_id or activity.boy_passport_id
        return activity.girl_passport_id if self.userInfo.sex == MODEL_SEX_MALE_INDEX else activity.boy_passport_id

    @timecost
    def getGuanguanList(self, longitude, latitude, limit):
        """优先展示自己参与的，其次有邀请人的，最后没有邀请人的，不分页直接返回最多20个"""
        matchedActivityList = []
        # 进行中的（且自己参与的）
        ongoingActivity = ActivityModel.getOngoingActivity(self.passportId)
        if ongoingActivity:  # 进行中的永远在第一位
            matchedActivityList.append(ongoingActivity)
        # 自己参与，但是没有闭环的
        unfinishedActivities = ActivityModel.getUnfinishedActivities(self.passportId)
        matchedActivityList.extend(unfinishedActivities)
        # 匹配的+兜底的
        hasLogin = bool(self.userInfo)
        matchedActivityIds = getMatchedActivityIds(self.userInfo) if hasLogin else set()
        notMatchedActivityIds = self.getActivityIdsByLocation(longitude, latitude, hasLogin, limit)   # 兜底的
        matchedActivityIds = matchedActivityIds.union(notMatchedActivityIds)
        matchedActivityList.extend(self.getLimitMatchedActivityList(matchedActivityIds, limit))
        # 封装
        addressMap = self.getAddressMapByIds(list(set(a.address_id for a in matchedActivityList)))
        matchUserMap = self.getMatchUserByIds(list(set(self.getMatchPassportId(a) for a in matchedActivityList)))
        guanguanList = []
        for activity in matchedActivityList:
            address = addressMap[activity.address_id]
            matchUser = matchUserMap.get(self.getMatchPassportId(activity), None)
            guanguanList.append(
                {
                    "id": activity.id,
                    "time": activity.startTimeStr,
                    "state": self.getState(activity),
                    "img": GuanHelper.getActivityImg(activity, address, matchUser, self.userInfo, True),
                    "address": address.nameShort,
                }
            )

        return guanguanList
