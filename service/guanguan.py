#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.activity import ActivityModel
from model.address import AddressModel
from model.requirement import RequirementModel
from model.user import UserModel
from ral.cache import checkCache
from service import BaseService
from util.class_helper import lazy_property
from util.const.base import ALL_STR
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_MAIL_TYPE_UNKNOWN
from util.const.qiniu_img import CDN_QINIU_ADDRESS_URL, CDN_QINIU_ADDRESS_IMG, CDN_QINIU_TIME_IMG


class GuanguanService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        super(GuanguanService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.passportId)

    def match(self, requirement):
        """对比 requirement 和 self.userInfo，进行一个匹配与否的判断"""
        # 1，如果 requirement为None，可以匹配
        if requirement is None:
            return True
        # 2，对比 requirement的每一个字段，只有所有字段要求，当前用户都符合，才算匹配
        if self.userInfo.sex != requirement.sex:
            return False
        if self.userInfo.martial_status != requirement.martial_status:
            return False
        if self.userInfo.birth_year < requirement.min_birth_year or self.userInfo.birth_year > requirement.max_birth_year:
            return False
        if self.userInfo.height < requirement.min_height or self.userInfo.height > requirement.max_height:
            return False
        if self.userInfo.weight < requirement.min_weight or self.userInfo.weight > requirement.max_weight:
            return False
        if self.userInfo.month_pay < requirement.min_month_pay or self.userInfo.month_pay > requirement.max_month_pay:
            return False
        if self.userInfo.home_province != requirement.home_province and requirement.home_province != ALL_STR:
            return False
        if self.userInfo.home_city != requirement.home_city and requirement.home_city != ALL_STR:
            return False
        if self.userInfo.home_area != requirement.home_area and requirement.home_area != ALL_STR:
            return False
        if self.userInfo.study_province != requirement.study_province and requirement.study_province != ALL_STR:
            return False
        if self.userInfo.study_city != requirement.study_city and requirement.study_city != ALL_STR:
            return False
        if self.userInfo.study_area != requirement.study_area and requirement.study_area != ALL_STR:
            return False
        if self.userInfo.school != requirement.school and requirement.school != ALL_STR:
            return False
        if self.userInfo.level != requirement.level and requirement.level != ALL_STR:
            return False
        if self.userInfo.major != requirement.major and requirement.major != ALL_STR:
            return False
        if self.userInfo.verify_type != requirement.verify_type and requirement.verify_type != MODEL_MAIL_TYPE_UNKNOWN:
            return False
        return True

    def getRequirementMap(self, activityList):
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
            if self.match(requirement):
                matchedActivityIdList.append(a.id)
        return matchedActivityIdList

    def getActivityList(self, longitude, latitude):
        addressIds = self.getAddressIds(longitude, latitude)
        if not addressIds:
            addressIds = [0]
        # 选择时空合适，时间倒序
        # 1. 符合空间条件的
        # 2. 符合时间未过期的
        # 3. 尚未邀请成功的
        activityList = ActivityModel.listByAddressIds(addressIds)
        return activityList

    @checkCache("GuanguanService:{passportId}", ex=60)
    def getMatchedActivityIdList(self, activityList=None, longitude="", latitude="", forceRefreshCache=False):  # todo 搞个离线脚本，异步定时循环每个passportid调用用这个方法，计算好
        """
        1. 按照邀请状态，以及时间倒排序
        2. 筛选掉不符合邀请人期望的
        """
        # 异步任务调用时，会强制刷新缓存，并且会对每个用户都传进来可能的活动。
        # 接口调用时，如果异步计算的缓存没有命中，就会根据用户当前的经纬度进行一个位置匹配查询可能的活动。
        if activityList is None:
            activityList = self.getActivityList(longitude, latitude)
        # 筛选掉不符合邀请人期望的
        return self.filterActivityIdList(activityList)

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
        """优先展示自己参与的，其次有邀请人的，最后没有邀请人的，不分页直接返回最多20个，todo 如果超过20个满足，需要有一种轮训机制展示"""
        matchedActivityIdList = self.getMatchedActivityIdList(longitude=longitude, latitude=latitude)
        matchedActivityList = self.getLimitMatchedActivityList(matchedActivityIdList)
        # todo 按照经纬度，对matchedActivityList进行排序
        ongoingActivity = ActivityModel.getOngoingActivity(self.passportId)
        if ongoingActivity:  # 进行中的永远在第一位
            matchedActivityList.insert(0, ongoingActivity)
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
                    "img": CDN_QINIU_ADDRESS_URL + address.img,
                    "addressImg": CDN_QINIU_ADDRESS_IMG,
                    "timeImg": CDN_QINIU_TIME_IMG,
                    "address": address.nameShort,
                }
            )

        return guanguanList
