#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
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
    PROGRESS_DESC,
    calc_activity_progress,
    calc_distance_km,
    calc_list_heart_kind,
    guanguan_list_sort_key,
    limit_solid_heart_items,
    should_show_guanguan_item,
)
from util.time_cost import timecost

logger = logging.getLogger(__name__)

UNKNOWN_NEGATIVE_ONE = -1
LIST_FETCH_POOL_FACTOR = 5


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
        列表规则：
        1. 心形优先级：实心 > 心碎 > 双心 > 单心 > 空白
        2. 同优先级按距离区间（每 10km 一档）由近到远
        3. 同区间内按见面时间由近到远
        4. 心碎/实心/双心永久展示；空白按距离只展示 N 小时内场次
        """
        if longitude == UNKNOWN_NEGATIVE_ONE or latitude == UNKNOWN_NEGATIVE_ONE:
            return [{
                "id": UNKNOWN_NEGATIVE_ONE,
                "time": "YYYY-MM-DD HH:mm",
                "state": "",
                "progressStatus": PROGRESS_NOT_SELECTED,
                "progressDesc": "",
                "heartKind": "empty",
                "img": DEFAULT_ADDRESS_URL,
                "address": "线下活动地址",
            }]

        UserModel.changeAllowLocation(self.passportId)
        now = datetime.datetime.now()
        pool_limit = max(limit * LIST_FETCH_POOL_FACTOR, limit)

        user_activities = ActivityModel.getUserAllActivities(self.passportId)
        user_activities_with_progress = [(a, self._calcActivityProgress(a)) for a in user_activities]
        participated_ids = {a.id for a, _ in user_activities_with_progress}

        sex = self.userInfo.sex if self.userInfo else MODEL_SEX_UNKNOWN_INDEX
        matched_activity_ids = (
            getMatchedActivityIds(self.userInfo) if sex != MODEL_SEX_UNKNOWN_INDEX else set()
        )
        candidate_activities = self.getCandidateActivities(longitude, latitude, pool_limit)
        candidate_with_progress = [
            (a, PROGRESS_NOT_SELECTED)
            for a in candidate_activities
            if a.id not in participated_ids
        ]

        all_activities = user_activities_with_progress + candidate_with_progress
        address_ids = list({a.address_id for a, _ in all_activities})
        address_map = self.getAddressMapByIds(address_ids)
        match_passport_ids = list({self.getMatchPassportId(a) for a, _ in all_activities})
        match_user_map = self.getMatchUserByIds(match_passport_ids)

        ranked_items = []
        for activity, progress in all_activities:
            address = address_map.get(activity.address_id)
            has_match = activity.id in matched_activity_ids
            heart_kind = calc_list_heart_kind(progress, has_match=has_match)
            distance_km = calc_distance_km(
                latitude, longitude,
                address.latitude if address else 0,
                address.longitude if address else 0,
            )
            minutes_until = None
            if activity.start_time:
                minutes_until = (activity.start_time - now).total_seconds() / 60.0
            if not should_show_guanguan_item(heart_kind, distance_km, minutes_until):
                continue
            ranked_items.append((
                guanguan_list_sort_key(heart_kind, distance_km, activity.start_time, now),
                activity,
                progress,
                heart_kind,
                address,
                match_user_map.get(self.getMatchPassportId(activity)),
            ))

        ranked_items.sort(key=lambda item: item[0])
        ranked_items = limit_solid_heart_items(ranked_items, lambda item: item[3])
        ranked_items = ranked_items[:limit]

        guanguan_list = []
        for _, activity, progress, heart_kind, address, match_user in ranked_items:
            guanguan_list.append({
                "id": activity.id,
                "time": activity.startTimeStr,
                "startTime": activity.start_time.strftime("%Y-%m-%d %H:%M") if activity.start_time else "",
                "progressStatus": progress,
                "progressDesc": PROGRESS_DESC.get(progress, ""),
                "heartKind": heart_kind,
                "img": GuanHelper.getActivityImg(activity, address, match_user, self.userInfo, True),
                "address": address.name if address else "",
                "longitude": address.longitude if address else 0,
                "latitude": address.latitude if address else 0,
            })
        return guanguan_list
