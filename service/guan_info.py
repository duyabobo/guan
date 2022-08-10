#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from model.activity import ActivityModel
from model.activity_change_record import ActivityChangeRecordModel
from model.address import AddressModel
from model.user import UserModel
from service import BaseService
from service.common.myself_helper import UserHelper
from service.myself import UserInfoService
from util.class_helper import lazy_property
from util.const.base import GUAN_INFO_OP_TYPE_QUIT, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_INVITE, \
    MODEL_MEET_RESULT_MAP
from util.const.mini_program import MYREQUIREMENT_PAGE, MYINFORMATION_PAGE_WITH_ERRMSG, \
    SUBSCRIBE_ACTIVITY_START_NOTI_TID
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX, MODEL_MEET_RESULT_CHOICE_LIST
from util.const.qiniu_img import CDN_QINIU_TIME_IMG, CDN_QINIU_ADDRESS_IMG, CDN_QINIU_UNKNOWN_HEAD_IMG, \
    CDN_QINIU_BOY_HEAD_IMG, CDN_QINIU_GIRL_HEAD_IMG, CDN_QINIU_ADDRESS_URL
from util.const.response import RESP_OK, RESP_NEED_FILL_INFO, RESP_JOIN_ACTIVITY_FAILED, RESP_HAS_ONGOING_ACTIVITY


class GuanInfoService(BaseService):
    def __init__(self, redis, activityId, passport):
        self.redis = redis
        self.activityId = activityId
        self.passport = passport
        self.passportId = passport.get('id', 0)
        self.activityRecord = None
        self.reloadActivityRecord()
        super(GuanInfoService, self).__init__(redis)

    @lazy_property
    def addressRecord(self):
        return AddressModel.getById(self.activityRecord.address_id)

    @lazy_property
    def oppositeUserRecord(self):
        user = UserModel.getByPassportId(self.passportId)
        if not user:
            return None
        elif user.sexIndex == MODEL_SEX_MALE_INDEX:
            passportId = self.activityRecord.girl_passport_id
        else:
            passportId = self.activityRecord.boy_passport_id

        return UserModel.getByPassportId(passportId)

    @property
    def timeIcon(self):
        return CDN_QINIU_TIME_IMG

    @property
    def addressIcon(self):
        return CDN_QINIU_ADDRESS_IMG

    @property
    def peopleImg(self):
        if not self.oppositeUserRecord:
            return CDN_QINIU_UNKNOWN_HEAD_IMG

        if self.oppositeUserRecord.sexIndex == MODEL_SEX_MALE_INDEX:
            return CDN_QINIU_BOY_HEAD_IMG
        elif self.oppositeUserRecord.sexIndex == MODEL_SEX_FEMALE_INDEX:
            return CDN_QINIU_GIRL_HEAD_IMG
        else:
            return CDN_QINIU_UNKNOWN_HEAD_IMG

    @property
    def img(self):
        return CDN_QINIU_ADDRESS_URL + self.addressRecord.img

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
            return GUAN_INFO_OP_TYPE_INVITE
        elif self.passportId in [self.activityRecord.girl_passport_id, self.activityRecord.boy_passport_id]:
            return GUAN_INFO_OP_TYPE_QUIT
        else:
            return GUAN_INFO_OP_TYPE_JOIN

    @property
    def opDesc(self):
        return {
            GUAN_INFO_OP_TYPE_INVITE: "发起邀请",
            GUAN_INFO_OP_TYPE_QUIT: "取消见面",
            GUAN_INFO_OP_TYPE_JOIN: "接受邀请",
        }.get(self.opType, "参加")

    @property
    def oppositePeopleInfos(self):
        if not self.oppositeUserRecord:
            return []

        informationList = UserHelper(self.redis, self.oppositeUserRecord).getInformationList()
        return [i.infoStr for i in informationList if i.infoStr]

    def getMeetResult(self):
        return {
            "value": MODEL_MEET_RESULT_MAP[self.activityRecord.meet_result],
            "selectValueIndex": self.activityRecord.meet_result,
            "choiceList": MODEL_MEET_RESULT_CHOICE_LIST,
        }
    
    def getGuanInfo(self):
        if self.opType != GUAN_INFO_OP_TYPE_QUIT:  # opType 是下一步操作类型
            subscribeTemplateIds = []
        else:
            subscribeTemplateIds = [SUBSCRIBE_ACTIVITY_START_NOTI_TID]
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
            "isAfterMeet": int(self.activityRecord.start_time < datetime.datetime.now()),
            "meetResultDesc": "点评内容只会被自己看到",
            "meetResult": self.getMeetResult(),
            "peopleImg": self.peopleImg,
            "people": "见面对象",
            "subscribeTemplateIds": subscribeTemplateIds,
            "myRequirementPage": MYREQUIREMENT_PAGE,
            "myInformationPage": MYINFORMATION_PAGE_WITH_ERRMSG,
            "requirementResult": "3人满足见面条件"  # todo
        }

    def reloadActivityRecord(self):
        self.activityRecord = ActivityModel.getById(self.activityId)

    @property
    def hasOngoingActivity(self):
        return bool(ActivityModel.getOngoingActivity(self.passportId))

    def activityOprete(self, opType):
        """对活动进行操作"""
        uis = UserInfoService(self.redis, self.passport)
        if not uis.userInfoIsFilled:
            return RESP_NEED_FILL_INFO
        if opType != self.opType:
            return RESP_JOIN_ACTIVITY_FAILED
        if self.hasOngoingActivity and \
                opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN]:  # 有进行中的活动，不能再次参与
            return RESP_HAS_ONGOING_ACTIVITY

        if opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN]:
            passportId = self.passportId
        else:
            passportId = 0
        updateParams = {}
        if uis.userInfo.sexIndex == MODEL_SEX_MALE_INDEX:
            updateParams['boy_passport_id'] = passportId
        elif uis.userInfo.sexIndex == MODEL_SEX_FEMALE_INDEX:
            updateParams['girl_passport_id'] = passportId
        ActivityModel.updateById(self.activityId, **updateParams)
        ActivityChangeRecordModel.addOne(self.activityId, self.passportId, opType)
        self.reloadActivityRecord()
        return RESP_OK  # todo 可以根据不同的场景，可以返回 RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI
