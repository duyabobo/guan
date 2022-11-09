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
from service.qiniu_cdn import MyStorage
from util.class_helper import lazy_property
from util.const.base import MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_FIT_AUTO, MODEL_MEET_RESULT_UNKNOWN
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_STATUS_YES
from util.time_cost import timecost


class GuanguanService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        super(GuanguanService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(passportId=self.passportId)

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

    @timecost
    @checkCache("GuanguanService:{passportId}", ex=60)
    def getActivityIdsByLocation(self, longitude, latitude):
        addressIds = self.getAddressIds(longitude, latitude)
        if not addressIds:
            addressIds = [0]
        activityIds = ActivityModel.listActivityIdsByAddressIds(addressIds)
        return set([a.id for a in activityIds])

    @timecost
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
            return 0
        return activity.girl_passport_id if self.userInfo.sex == MODEL_SEX_MALE_INDEX else activity.boy_passport_id

    def getMatchMeetResult(self, activity):
        if not self.userInfo:
            return MODEL_MEET_RESULT_UNKNOWN
        return activity.girl_meet_result if self.userInfo.sex == MODEL_SEX_MALE_INDEX else activity.boy_meet_result

    def getActivityImg(self, activity, address, matchUser):
        if not matchUser or matchUser.has_head_img != MODEL_STATUS_YES:  # 如果没有异性参与，或者用户没有选择头像，返回地址图片
            return address.thumbnails_img
        if self.getMatchMeetResult(activity) in [MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_FIT_AUTO]:  # 如果双方都满意此次见面，就返回异性真实头像
            return MyStorage.getRealThumbnailsImgUrl(matchUser.passportId, matchUser.head_img_version)
        else:
            return MyStorage.getVirtualThumbnailsImgUrl(matchUser.passportId, matchUser.head_img_version)

    @timecost
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
                    "img": self.getActivityImg(activity, address, matchUser),
                    "address": address.nameShort,
                }
            )

        return guanguanList
