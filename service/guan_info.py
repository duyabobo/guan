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
    def userRecord(self):
        if self.opType in [const.GUAN_INFO_OP_TYPE_INVITE, const.GUAN_INFO_OP_TYPE_INVITE_QUIT]:
            passportId = self.activityRecord.boy_passport_id
        else:
            passportId = self.activityRecord.girl_passport_id
        return UserModel.getByPassportId(self.dbSession, passportId)

    @property
    def timeIcon(self):
        return const.CDN_QINIU_TIME_IMG

    @property
    def addressIcon(self):
        return const.CDN_QINIU_ADDRESS_IMG

    @property
    def peopleImg(self):
        if not self.userRecord:
            return const.CDN_QINIU_UNKNOWN_HEAD_IMG

        if self.userRecord.sex == const.MODEL_SEX_MALE:
            return const.CDN_QINIU_BOY_HEAD_IMG
        elif self.userRecord.sex == const.MODEL_SEX_FEMALE:
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
        if not self.activityRecord.girl_passport_id:
            return const.GUAN_INFO_OP_TYPE_INVITE
        elif self.activityRecord.girl_passport_id == self.passportId and self.activityRecord.boy_passport_id:
            return const.GUAN_INFO_OP_TYPE_INVITE_QUIT_AFTER_ACCEPT
        elif self.activityRecord.girl_passport_id == self.passportId:
            return const.GUAN_INFO_OP_TYPE_INVITE_QUIT
        elif not self.activityRecord.boy_passport_id:
            return const.GUAN_INFO_OP_TYPE_ACCEPT
        elif self.activityRecord.boy_passport_id == self.passportId:
            return const.GUAN_INFO_OP_TYPE_ACCEPT_QUIT
        else:
            return const.GUAN_INFO_OP_TYPE_ACCEPT_UNKNOWN

    @property
    def opDesc(self):
        return {
            const.GUAN_INFO_OP_TYPE_INVITE: "发起邀请",
            const.GUAN_INFO_OP_TYPE_INVITE_QUIT: "取消邀请",
            const.GUAN_INFO_OP_TYPE_ACCEPT: "接受邀请",
            const.GUAN_INFO_OP_TYPE_ACCEPT_QUIT: "请准时参加，或联系客服取消",
            const.GUAN_INFO_OP_TYPE_INVITE_QUIT_AFTER_ACCEPT: "请准时参加，或联系客服取消",
        }.get(self.opType, "敬请期待")

    @property
    def peopleInfos(self):
        if not self.userRecord:
            return []

        matchHelper = MatchHelper(self.userRecord)
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
        return {
            "img": self.img,
            "address": self.address,
            "addressDesc": self.addressDesc,
            "time": self.time,
            "timeDesc": self.timeDesc,
            "guanId": self.activityId,
            "peopleInfos": self.peopleInfos,
            "opDesc": self.opDesc,
            "opType": self.opType,
            "timeImg": self.timeIcon,
            "addressImg": self.addressIcon,
            "peopleImg": self.peopleImg,
            "people": "相亲对象",
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
                opType in [const.GUAN_INFO_OP_TYPE_INVITE, const.GUAN_INFO_OP_TYPE_ACCEPT]:  # 有进行中的活动，不能再次参与
            return const.RESP_HAS_ONGOING_ACTIVITY
        updateParams = {}
        if opType == const.GUAN_INFO_OP_TYPE_INVITE:
            updateParams['girl_passport_id'] = self.passportId
        elif opType == const.GUAN_INFO_OP_TYPE_ACCEPT:
            updateParams['boy_passport_id'] = self.passportId
        elif opType == const.GUAN_INFO_OP_TYPE_INVITE_QUIT:
            updateParams['girl_passport_id'] = 0
        elif opType == const.GUAN_INFO_OP_TYPE_ACCEPT_QUIT:
            updateParams['boy_passport_id'] = 0
        elif opType == const.GUAN_INFO_OP_TYPE_INVITE_QUIT_AFTER_ACCEPT:
            updateParams['girl_passport_id'] = self.activityRecord.boy_passport_id
            updateParams['boy_passport_id'] = 0
        ActivityModel.updateById(self.dbSession, self.activityId, **updateParams)
        ActivityChangeRecordModel.addOne(self.dbSession, self.activityId, self.passportId, opType)
        if opType == const.GUAN_INFO_OP_TYPE_INVITE_QUIT_AFTER_ACCEPT:
            ActivityChangeRecordModel.addOne(self.dbSession, self.activityId, self.activityRecord.boy_passport_id,
                                             const.GUAN_INFO_OP_TYPE_ACCEPT_BECOME_INVITE)
        self.reloadActivityRecord()
        return const.RESP_OK  # todo 可以根据不同的场景，可以返回 RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI
