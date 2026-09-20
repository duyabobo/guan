#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.activity import ActivityModel
from model.address import AddressModel
from model.user import UserModel
from ral.activity import getMatchedActivityIds
from ral.cache import checkCache
from service import BaseService
from service.common.guan_helper import GuanHelper
from util.class_helper import lazy_property
from util.const.match import (
    MODEL_SEX_MALE_INDEX, MODEL_SEX_UNKNOWN_INDEX,
    MODEL_ACTIVITY_STATE_EMPTY, MODEL_ACTIVITY_STATE_INVITING,
    DEFAULT_ADDRESS_URL
)
from util.const.progress import (
    PROGRESS_NOT_SELECTED,
    PROGRESS_DESC, PROGRESS_SORT_WEIGHT,
    calc_activity_progress
)
from util.time_cost import timecost

logger = logging.getLogger(__name__)

UNKNOWN_NEGATIVE_ONE = -1


class GuanguanService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        super(GuanguanService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    def _calcActivityProgress(self, activity):
        """计算进展状态（委托纯函数）"""
        return calc_activity_progress(self.passportId, activity)

    @timecost
    def getActivityIdsByLocation(self, longitude, latitude, limit):
        if not longitude and not latitude:
            addressIds = []
        else:
            addressIds = self.getAddressIds(longitude=round(longitude, 2), latitude=round(latitude, 2), limit=limit * 10)
        emptyActivityIds = ActivityModel.listActivityIdsByAddressIds(addressIds, MODEL_ACTIVITY_STATE_EMPTY, limit)
        invitingActivityIds = ActivityModel.listActivityIdsByAddressIds(addressIds, MODEL_ACTIVITY_STATE_INVITING, limit)
        return set([a.id for a in emptyActivityIds]), set([a.id for a in invitingActivityIds])

    @timecost
    def getLimitMatchedActivityList(self, matchedActivityIdsSet, locationFreeActivityIdsSet, locationMatchingActivityIdsSet, sex, limit):
        matchedLocationActivityIdsSet = matchedActivityIdsSet.intersection(locationMatchingActivityIdsSet)
        if len(matchedLocationActivityIdsSet) < limit:
            sortedActivityIdList = list(matchedLocationActivityIdsSet)
            sortedActivityIdList.extend(list(matchedActivityIdsSet - set(sortedActivityIdList)))
            if sex == MODEL_SEX_UNKNOWN_INDEX:
                sortedActivityIdList.extend(list(locationFreeActivityIdsSet.union(locationMatchingActivityIdsSet) - set(sortedActivityIdList)))
            else:
                sortedActivityIdList.extend(list(locationFreeActivityIdsSet - set(sortedActivityIdList)))
        else:
            sortedActivityIdList = list(matchedLocationActivityIdsSet)
        return ActivityModel.listActivity(sortedActivityIdList[:limit], exceptPassportId=self.passportId)

    @timecost
    @checkCache("GuanguanService:{longitude}:{latitude}:{limit}")
    def getAddressIds(self, longitude, latitude, limit):
        addressList = AddressModel.listByLongitudeLatitude(longitude, latitude)
        addressIdMapDistance = {
            a.id: (a.longitude - longitude) ** 2 + (a.latitude - latitude) ** 2
            for a in addressList
        }
        return [k for k, v in sorted(addressIdMapDistance.items(), key=lambda x: x[1])][:limit]

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
    def getCandidateActivities(self, longitude, latitude, limit):
        """获取候选活动（用户未参与的推荐活动）"""
        sex = self.userInfo.sex if self.userInfo else MODEL_SEX_UNKNOWN_INDEX
        matchedActivityIdsSet = getMatchedActivityIds(self.userInfo) if sex != MODEL_SEX_UNKNOWN_INDEX else set()
        locationFreeActivityIdsSet, locationMatchingActivityIdsSet = self.getActivityIdsByLocation(longitude, latitude, limit)
        return self.getLimitMatchedActivityList(
            matchedActivityIdsSet, locationFreeActivityIdsSet, locationMatchingActivityIdsSet, sex, limit
        )

    @timecost
    def getGuanguanList(self, longitude, latitude, limit):
        """
        列表排序规则（优先级从高到低）：
        AGREE/DISAGREE（常驻）→ MET → WAIT_MEET → SELECTED → NOT_SELECTED（按地理时间综合排序）
        """
        if longitude == UNKNOWN_NEGATIVE_ONE or latitude == UNKNOWN_NEGATIVE_ONE:
            return [{
                "id": UNKNOWN_NEGATIVE_ONE,
                "time": "YYYY-MM-DD HH:mm",
                "state": "",
                "progressStatus": PROGRESS_NOT_SELECTED,
                "progressDesc": "",
                "img": DEFAULT_ADDRESS_URL,
                "address": "线下活动地址",
            }]

        UserModel.changeAllowLocation(self.passportId)

        # 1. 用户已参与的所有活动（含各状态）
        user_activities = ActivityModel.getUserAllActivities(self.passportId)
        user_activities_with_progress = [(a, self._calcActivityProgress(a)) for a in user_activities]

        # 2. 候选活动（用户未参与）
        participated_ids = {a.id for a, _ in user_activities_with_progress}
        candidate_activities = self.getCandidateActivities(longitude, latitude, limit)
        candidate_with_progress = [
            (a, PROGRESS_NOT_SELECTED)
            for a in candidate_activities
            if a.id not in participated_ids
        ]

        # 3. 合并并按进展状态权重排序
        all_activities = user_activities_with_progress + candidate_with_progress
        all_activities.sort(key=lambda x: PROGRESS_SORT_WEIGHT.get(x[1], 0), reverse=True)
        all_activities = all_activities[:limit]

        # 4. 批量获取地址和关联用户（避免 N+1 查询）
        addressIds = list({a.address_id for a, _ in all_activities})
        addressMap = self.getAddressMapByIds(addressIds)
        matchPassportIds = list({self.getMatchPassportId(a) for a, _ in all_activities})
        matchUserMap = self.getMatchUserByIds(matchPassportIds)

        # 5. 封装返回列表
        guanguanList = []
        for activity, progress in all_activities:
            address = addressMap.get(activity.address_id)
            matchUser = matchUserMap.get(self.getMatchPassportId(activity))
            guanguanList.append({
                "id": activity.id,
                "time": activity.startTimeStr,
                "progressStatus": progress,
                "progressDesc": PROGRESS_DESC.get(progress, ""),
                "img": GuanHelper.getActivityImg(activity, address, matchUser, self.userInfo, True),
                "address": address.name if address else "",
            })

        return guanguanList
