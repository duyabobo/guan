#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from model.activity import ActivityModel
from model.activity_change_record import ActivityChangeRecordModel
from model.address import AddressModel
from model.user import UserModel
from service import BaseService
from service.common.match import MatchHelper
from service.myself import UserInfoService
from util import const
from util.class_helper import lazy_property


class GuanInfoService(BaseService):
    def __init__(self, dbSession, redis, activityId, passport):
        self.dbSession = dbSession
        self.redis = redis
        self.activityId = activityId
        self.passport = passport
        self.passportId = passport.get('id', 0)
        self.activityRecord = None
        self.reloadActivityRecord()
        super(GuanInfoService, self).__init__(dbSession, redis)

    @lazy_property
    def addressRecord(self):
        return AddressModel.getById(self.dbSession, self.activityRecord.address_id)

    @lazy_property
    def oppositeUserRecord(self):
        user = UserModel.getByPassportId(self.dbSession, self.passportId)
        if user.sexIndex == const.MODEL_SEX_MALE_INDEX:
            passportId = self.activityRecord.girl_passport_id
        else:
            passportId = self.activityRecord.boy_passport_id

        return UserModel.getByPassportId(self.dbSession, passportId)

    @property
    def timeIcon(self):
        return const.CDN_QINIU_TIME_IMG

    @property
    def addressIcon(self):
        return const.CDN_QINIU_ADDRESS_IMG

    @property
    def peopleImg(self):
        if not self.oppositeUserRecord:
            return const.CDN_QINIU_UNKNOWN_HEAD_IMG

        if self.oppositeUserRecord.sexIndex == const.MODEL_SEX_MALE_INDEX:
            return const.CDN_QINIU_BOY_HEAD_IMG
        elif self.oppositeUserRecord.sexIndex == const.MODEL_SEX_FEMALE_INDEX:
            return const.CDN_QINIU_GIRL_HEAD_IMG
        else:
            return const.CDN_QINIU_UNKNOWN_HEAD_IMG

    @property
    def img(self):
        return const.CDN_QINIU_ADDRESS_URL + self.addressRecord.img

    @property
    def address(self):
        return self.addressRecord.nameLong

    @property
    def addressDesc(self):
        return self.addressRecord.description

    @property
    def time(self):
        return self.activityRecord.startTimeStr

    @property
    def timeDesc(self):
        startTime = self.activityRecord.start_time
        today = datetime.datetime.now().date()

        leftDays = (startTime.date() - today).days
        if leftDays == 0:
            return "今天"
        elif leftDays == 1:
            return "明天"
        elif leftDays == 2:
            return "后天"
        else:
            return "%s天后" % leftDays

    @property
    def opType(self):
        if not self.activityRecord.boy_passport_id and not self.activityRecord.girl_passport_id:
            return const.GUAN_INFO_OP_TYPE_INVITE
        elif self.passportId in [self.activityRecord.girl_passport_id, self.activityRecord.boy_passport_id]:
            return const.GUAN_INFO_OP_TYPE_QUIT
        else:
            return const.GUAN_INFO_OP_TYPE_JOIN

    @property
    def opDesc(self):
        return {
            const.GUAN_INFO_OP_TYPE_INVITE: "发起邀请",
            const.GUAN_INFO_OP_TYPE_QUIT: "取消见面",
            const.GUAN_INFO_OP_TYPE_JOIN: "接受邀请",
        }.get(self.opType, "参加")

    @property
    def oppositePeopleInfos(self):
        if not self.oppositeUserRecord:
            return []

        matchHelper = MatchHelper(self.oppositeUserRecord)
        allInfos = [
            matchHelper.sexValue,
            "出生于%d年" % matchHelper.birthYearValue,
            matchHelper.martialStatusValue,
            "身高%scm" % matchHelper.heightValue,
            "体重%skg" % matchHelper.weightValue,
            "月收入(税前)%s元" % matchHelper.monthPayValue,
            matchHelper.educationValue,
        ]
        return [i for i in allInfos if i]
    
    def getGuanInfo(self):
        if self.opType != const.GUAN_INFO_OP_TYPE_QUIT:  # opType 是下一步操作类型
            subscribeTemplateIds = []
        else:
            subscribeTemplateIds = [const.SUBSCRIBE_ACTIVITY_START_NOTI_TID]
        return {
            "img": self.img,
            "address": self.address,
            "addressDesc": self.addressDesc,
            "time": self.time,
            "timeDesc": self.timeDesc,
            "guanId": self.activityId,
            "oppositePeopleInfos": self.oppositePeopleInfos,
            "opDesc": self.opDesc,
            "opType": self.opType,
            "timeImg": self.timeIcon,
            "addressImg": self.addressIcon,
            "peopleImg": self.peopleImg,
            "people": "见面对象",
            "subscribeTemplateIds": subscribeTemplateIds,
            "myRequirementPage": const.MYREQUIREMENT_PAGE,
            "myInformationPage": const.MYINFORMATION_PAGE_WITH_ERRMSG,
            "requirementResult": "3人满足见面条件"  # todo
        }

    def reloadActivityRecord(self):
        self.activityRecord = ActivityModel.getById(self.dbSession, self.activityId)

    @property
    def hasOngoingActivity(self):
        return bool(ActivityModel.getOngoingActivity(self.dbSession, self.passportId))

    def activityOprete(self, opType):
        """对活动进行操作"""
        uis = UserInfoService(self.dbSession, self.redis, self.passport)
        if not uis.userInfoIsFilled:
            return const.RESP_NEED_FILL_INFO
        if opType != self.opType:
            return const.RESP_JOIN_ACTIVITY_FAILED
        if self.hasOngoingActivity and \
                opType in [const.GUAN_INFO_OP_TYPE_INVITE, const.GUAN_INFO_OP_TYPE_JOIN]:  # 有进行中的活动，不能再次参与
            return const.RESP_HAS_ONGOING_ACTIVITY

        if opType in [const.GUAN_INFO_OP_TYPE_INVITE, const.GUAN_INFO_OP_TYPE_JOIN]:
            passportId = self.passportId
        else:
            passportId = 0
        updateParams = {}
        if uis.userInfo.sexIndex == const.MODEL_SEX_MALE_INDEX:
            updateParams['boy_passport_id'] = passportId
        elif uis.userInfo.sexIndex == const.MODEL_SEX_FEMALE_INDEX:
            updateParams['girl_passport_id'] = passportId
        ActivityModel.updateById(self.dbSession, self.activityId, **updateParams)
        ActivityChangeRecordModel.addOne(self.dbSession, self.activityId, self.passportId, opType)
        self.reloadActivityRecord()
        return const.RESP_OK  # todo 可以根据不同的场景，可以返回 RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI
