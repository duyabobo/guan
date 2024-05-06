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
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_SEX_UNKNOWN_INDEX, MODEL_ACTIVITY_STATE_EMPTY, \
    MODEL_ACTIVITY_STATE_INVITING, DEFAULT_ADDRESS_URL
from util.time_cost import timecost


UNKNOWN_NEGATIVE_ONE = -1


class GuanguanService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        super(GuanguanService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    @timecost
    def getActivityIdsByLocation(self, longitude, latitude, limit):
        if not longitude and not latitude:  # 没有获取地址信息
            addressIds = []
        else:  # 有获取地址信息
            addressIds = self.getAddressIds(longitude=round(longitude, 2), latitude=round(latitude, 2), limit=limit*10)
        emptyActivityIds = ActivityModel.listActivityIdsByAddressIds(addressIds, MODEL_ACTIVITY_STATE_EMPTY, limit)
        invitingActivityIds = ActivityModel.listActivityIdsByAddressIds(addressIds, MODEL_ACTIVITY_STATE_INVITING, limit)
        return set([a.id for a in emptyActivityIds]), set([a.id for a in invitingActivityIds])

    @timecost
    def getLimitMatchedActivityList(self, matchedActivityIdsSet, locationFreeActivityIdsSet, locationMatchingActivityIdsSet, sex, limit):
        matchedLocationActivityIdsSet = matchedActivityIdsSet.intersection(locationMatchingActivityIdsSet)
        if len(matchedLocationActivityIdsSet) < limit:  # 附近匹配不足
            # 附近匹配的（高优）
            sortedActivityIdList = list(matchedLocationActivityIdsSet)
            # 匹配的（次高优）
            sortedActivityIdList.extend(list(matchedActivityIdsSet - set(sortedActivityIdList)))
            # 附近的（补充）
            if sex == MODEL_SEX_UNKNOWN_INDEX:  # 性别未定，匹配中的和空闲的活动都可以用来补充
                sortedActivityIdList.extend(list(locationFreeActivityIdsSet.union(locationMatchingActivityIdsSet) - set(sortedActivityIdList)))
            else:  # 性别已定，只补充空闲的活动
                sortedActivityIdList.extend(list(locationFreeActivityIdsSet - set(sortedActivityIdList)))
        else:
            sortedActivityIdList = list(matchedLocationActivityIdsSet)
        return ActivityModel.listActivity(sortedActivityIdList[:limit], exceptPassportId=self.passportId)

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
        if longitude == UNKNOWN_NEGATIVE_ONE or latitude == UNKNOWN_NEGATIVE_ONE:  # 尚未获取用户地理位置，此时返回功能介绍类数据demo
            return (
                [
                    {
                        "id": UNKNOWN_NEGATIVE_ONE,
                        "time": "YYYY-MM-DD HH:mm:SS",
                        "state": "",
                        "img": DEFAULT_ADDRESS_URL,
                        "address": "根据地理位置进行活动推荐。",
                    }
                ]
            )


        # 记录用户已经允许获取地理位置
        UserModel.changeAllowLocation(self.passportId)

        matchedActivityList = []
        # 自己参与，已表达意愿为满意发展中
        ongoingActivity = ActivityModel.getOngoingActivity(self.passportId)
        if ongoingActivity:  # 有发展中的
            matchedActivityList.append(ongoingActivity)
        else:
            # 自己参与，未表达意愿为满意发展中（邀请中/邀请成功尚未见面的/见面后尚未表达意愿）
            unfinishedActivities = ActivityModel.getUnfinishedActivities(self.passportId)
            matchedActivityList.extend(unfinishedActivities)
            # 匹配的+兜底的
            sex = self.userInfo.sex if self.userInfo else MODEL_SEX_UNKNOWN_INDEX
            matchedActivityIdsSet = getMatchedActivityIds(self.userInfo) if sex != MODEL_SEX_UNKNOWN_INDEX else set()
            locationFreeActivityIdsSet, locationMatchingActivityIdsSet = self.getActivityIdsByLocation(longitude, latitude, limit)   # 兜底的
            limitMatchedActivityList = self.getLimitMatchedActivityList(matchedActivityIdsSet, locationFreeActivityIdsSet, locationMatchingActivityIdsSet, sex, limit)
            matchedActivityList.extend(limitMatchedActivityList)
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
                    "address": address.name,
                }
            )

        return guanguanList
