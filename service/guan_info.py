#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from model.activity import ActivityModel
from model.address import AddressModel
from model.user import UserModel
from service import BaseService
from service.common.match import MatchHelper
from util import const
from util.class_helper import lazy_property


class GuanInfoService(BaseService):
    def __init__(self, dbSession, redis, activityId, passportId):
        self.dbSession = dbSession
        self.redis = redis
        self.activityId = activityId
        self.passportId = passportId
        self.activityRecord = None
        self.reloadActivityRecord()
        super(GuanInfoService, self).__init__(dbSession, redis)

    @lazy_property
    def addressRecord(self):
        return AddressModel.getById(self.dbSession, self.activityRecord.address_id)

    @lazy_property
    def userRecord(self):
        return UserModel.getByPassportId(self.dbSession, self.activityRecord.invite_passport_id)

    @property
    def timeIcon(self):
        return const.CDN_QINIU_URL + "time.jpeg"

    @property
    def addressIcon(self):
        return const.CDN_QINIU_URL + "address.jpeg"

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
        return const.CDN_QINIU_URL + self.addressRecord.img

    @property
    def address(self):
        return self.addressRecord.name

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
        if not self.activityRecord.invite_passport_id:
            return const.GUAN_INFO_OP_TYPE_INVITE
        elif self.activityRecord.invite_passport_id == self.passportId:
            return const.GUAN_INFO_OP_TYPE_INVITE_QUIT
        elif not self.activityRecord.accept_passport_id:
            return const.GUAN_INFO_OP_TYPE_ACCEPT
        elif self.activityRecord.accept_passport_id == self.passportId:
            return const.GUAN_INFO_OP_TYPE_ACCEPT_QUIT
        else:
            return const.GUAN_INFO_OP_TYPE_ACCEPT_UNKNOWN

    @property
    def opDesc(self):
        return {
            const.GUAN_INFO_OP_TYPE_INVITE: "发起邀请",
            const.GUAN_INFO_OP_TYPE_INVITE_QUIT: "收回邀请",
            const.GUAN_INFO_OP_TYPE_ACCEPT: "接受邀请",
            const.GUAN_INFO_OP_TYPE_ACCEPT_QUIT: "取消邀请",
        }.get(self.opType, "敬请期待")

    @property
    def peopleInfos(self):
        if not self.userRecord:
            return []

        matchHelper = MatchHelper(self.userRecord)
        allInfos = [
            matchHelper.sexValue,
            matchHelper.birthYearValue,
            matchHelper.martialStatus,
            matchHelper.height,
            matchHelper.weight,
            matchHelper.monthPay,
            matchHelper.education,
        ]
        return [i for i in allInfos if i]
    
    def getGuanInfo(self):
        return {
            "img": self.img,
            "address": self.address,
            "addressDesc": self.addressDesc,
            "addressInfos": [],  # todo
            "time": self.time,
            "timeInfos": [],  # todo
            "timeDesc": self.timeDesc,
            "guanId": self.activityId,
            "peopleInfos": self.peopleInfos,
            "opDesc": self.opDesc,
            "opType": self.opType,
            "timeImg": self.timeIcon,
            "addressImg": self.addressIcon,
            "peopleImg": self.peopleImg,
            "people": "人物",  # todo 相亲对象
        }

    def reloadActivityRecord(self):
        self.activityRecord = ActivityModel.getById(self.dbSession, self.activityId)

    def activityOprete(self, opType):
        """对活动进行操作"""
        pass  # todo
        self.reloadActivityRecord()
