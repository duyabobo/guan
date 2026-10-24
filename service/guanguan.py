#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

from model.activity import ActivityModel
from model.address import AddressModel
from ral.cache import checkCache
from service import BaseService
from service.common.guan_helper import GuanHelper
from service.common.meet_outcome import settle_due_meets
from service.common.profile_match import ProfileMatchService
from util.const.match import (
    MODEL_SEX_UNKNOWN_INDEX,
    MODEL_ACTIVITY_STATE_EMPTY, MODEL_ACTIVITY_STATE_INVITING,
    DEFAULT_ADDRESS_URL
)
from util.const.progress import (
    PROGRESS_NOT_SELECTED,
    PROGRESS_DESC,
    calc_activity_progress,
    calc_distance_km,
    calc_list_has_match,
    calc_list_heart_kind,
    guanguan_list_sort_key,
    limit_solid_heart_items,
    should_include_activity_for_match,
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
    def getCandidateActivities(self, longitude, latitude, limit):
        """先按地点取出候选，匹配与否在列表组装时用 profile_attr 判断。"""
        location_free, location_matching = self.getActivityIdsByLocation(longitude, latitude, limit)
        return self.getLimitMatchedActivityList(
            set(), location_free, location_matching, MODEL_SEX_UNKNOWN_INDEX, limit
        )

    @timecost
    def getGuanguanList(self, longitude, latitude, limit):
        """
        列表规则：
        1. 心形：实心 > 心碎 > 双心 > 单心 > 无心
        2. 同级按距离档（每 10km 一级）由近到远
        3. 同档按见面时间由近到远
        4. 心碎/实心/双心永久展示
        5. 还没约上的：两周内、100km 内、匹配通过，且每 10km 只留 1 小时
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

        now = datetime.datetime.now()
        pool_limit = max(limit * LIST_FETCH_POOL_FACTOR, limit)
        settle_due_meets(self.passportId)

        user_activities = ActivityModel.getUserAllActivities(self.passportId)
        user_activities_with_progress = [(a, self._calcActivityProgress(a)) for a in user_activities]
        participated_ids = {a.id for a, _ in user_activities_with_progress}

        candidate_activities = self.getCandidateActivities(longitude, latitude, pool_limit)
        matched_activity_ids = ProfileMatchService.matched_activity_ids(self.passportId, candidate_activities)
        candidate_with_progress = [
            (a, PROGRESS_NOT_SELECTED)
            for a in candidate_activities
            if a.id not in participated_ids
        ]

        all_activities = user_activities_with_progress + candidate_with_progress
        address_ids = list({a.address_id for a, _ in all_activities})
        address_map = self.getAddressMapByIds(address_ids)

        ranked_items = []
        for activity, progress in all_activities:
            if not should_include_activity_for_match(
                progress, activity.id, activity.state, matched_activity_ids, MODEL_ACTIVITY_STATE_EMPTY,
            ):
                continue
            address = address_map.get(activity.address_id)
            has_match = calc_list_has_match(progress, activity.state, activity.id in matched_activity_ids)
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
            ))

        ranked_items.sort(key=lambda item: item[0])
        ranked_items = limit_solid_heart_items(ranked_items, lambda item: item[3])
        ranked_items = ranked_items[:limit]

        guanguan_list = []
        for _, activity, progress, heart_kind, address in ranked_items:
            guanguan_list.append({
                "id": activity.id,
                "time": activity.startTimeStr,
                "startTime": activity.start_time.strftime("%Y-%m-%d %H:%M") if activity.start_time else "",
                "progressStatus": progress,
                "progressDesc": PROGRESS_DESC.get(progress, ""),
                "heartKind": heart_kind,
                "hasMatch": calc_list_has_match(progress, activity.state, activity.id in matched_activity_ids),
                "img": GuanHelper.getActivityImg(address, True),
                "address": address.name if address else "",
                "longitude": address.longitude if address else 0,
                "latitude": address.latitude if address else 0,
            })
        return guanguan_list
