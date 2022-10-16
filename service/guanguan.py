#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.activity import ActivityModel
from model.address import AddressModel
from model.requirement import RequirementModel
from model.user import UserModel
from ral.activity import getMatchedActivityIds
from ral.cache import checkCache
from service import BaseService
from service.common.match import MatchHelper
from util.class_helper import lazy_property
from util.const.match import MODEL_SEX_MALE_INDEX
from util.const.qiniu_img import CDN_QINIU_ADDRESS_IMG, CDN_QINIU_TIME_IMG


class GuanguanService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        super(GuanguanService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.passportId)

    def getRequirementMap(self, activityList):
        if not self.userInfo:
            return {}
        getPid = lambda x: a.girl_passport_id if self.userInfo.sex == MODEL_SEX_MALE_INDEX else a.boy_passport_id
        passportIds = [getPid(a) for a in activityList]
        if not passportIds:
            return {}
        requirementList = RequirementModel.getByPassportIds(list(set(passportIds)))
        passportIdMapRequirement = {r.passport_id: r for r in requirementList}
        activityIdMapPassportId = {a.id: getPid(a) for a in activityList}
        return {aid: passportIdMapRequirement.get(activityIdMapPassportId[aid], None) for aid in activityIdMapPassportId}

    def filterActivityIdList(self, activityList):
        """筛选匹配满足的"""
        activityIdMapRequirement = self.getRequirementMap(activityList)
        matchedActivityIdList = []
        for a in activityList:
            requirement = activityIdMapRequirement.get(a.id, None)
            if MatchHelper.match(self.userInfo, requirement):
                matchedActivityIdList.append(a.id)
        return matchedActivityIdList

    @checkCache("GuanguanService:{passportId}", ex=60)
    def getActivityIdsByLocation(self, longitude, latitude):
        addressIds = self.getAddressIds(longitude, latitude)
        if not addressIds:
            addressIds = [0]
        activityIds = ActivityModel.listActivityIdsByAddressIds(addressIds)
        return set([a.id for a in activityIds])

    def getLimitMatchedActivityList(self, activityIds, limit=20):
        return ActivityModel.listActivity(activityIds, limit, exceptPassportId=self.passportId)

    def getAddressIds(self, longitude, latitude):
        addressList = AddressModel.listByLongitudeLatitude(longitude, latitude)  # 根据地理位置查
        return [a.id for a in addressList]

    def getState(self, activity):
        girl_pid = activity.girl_passport_id
        boy_pid = activity.boy_passport_id
        if not girl_pid and not boy_pid:
            return "虚位以待"
        elif self.passportId in [girl_pid, boy_pid]:
            return "我的见面"
        else:
            return "见面邀请"

    def getAddressMapByIds(self, addressIds):
        if not addressIds:
            return {}
        addressList = AddressModel.listByIds(addressIds)
        return {a.id: a for a in addressList}

    def getGuanguanList(self, longitude, latitude):
        """优先展示自己参与的，其次有邀请人的，最后没有邀请人的，不分页直接返回最多20个"""
        matchedActivityList = []
        # 进行中的（且自己参与的）
        ongoingActivity = ActivityModel.getOngoingActivity(self.passportId)
        if ongoingActivity:  # 进行中的永远在第一位
            matchedActivityList.append(ongoingActivity)
        # 自己参与，但是没有闭环的
        unfinishedActivities = ActivityModel.getUnfinishedActivities(self.passportId)
        matchedActivityList.extend(unfinishedActivities)
        # 匹配的
        matchedActivityIds = getMatchedActivityIds(self.userInfo) if self.userInfo else set()
        matchedActivityIds = matchedActivityIds.union(self.getActivityIdsByLocation(longitude=longitude, latitude=latitude))  # 兜底的
        matchedActivityList.extend(self.getLimitMatchedActivityList(matchedActivityIds))  # 按照经纬度，对matchedActivityList进行排序--- 不太必要，同城即可，后期还会加上学校
        # 封装
        addressMap = self.getAddressMapByIds(list(set(a.address_id for a in matchedActivityList)))
        guanguanList = []
        for activity in matchedActivityList:
            address = addressMap[activity.address_id]
            guanguanList.append(
                {
                    "id": activity.id,
                    "time": activity.startTimeStr,
                    "boyImg": activity.boyImg,
                    "girlImg": activity.girlImg,
                    "state": self.getState(activity),
                    "img": address.thumbnails_img,
                    "addressImg": CDN_QINIU_ADDRESS_IMG,
                    "timeImg": CDN_QINIU_TIME_IMG,
                    "address": address.nameShort,
                }
            )

        return guanguanList
