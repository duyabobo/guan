#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from model.activity import ActivityModel
from model.activity_change_record import ActivityChangeRecordModel
from model.address import AddressModel
from model.requirement import RequirementModel, UNREACHABLE_REQUIREMENT
from model.user import UserModel
from ral.activity import changeByRequirement
from ral.cache import lock
from service import BaseService
from service.common.match import MatchHelper
from service.common.myself_helper import UserHelper
from service.myself import UserInfoService
from util.class_helper import lazy_property
from util.const.base import GUAN_INFO_OP_TYPE_QUIT, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_INVITE, \
    MODEL_MEET_RESULT_MAP
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX, MODEL_MEET_RESULT_CHOICE_LIST, \
    MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_EMPTY, MODEL_ACTIVITY_STATE_INVITE_SUCCESS
from util.const.mini_program import MYREQUIREMENT_PAGE, MYINFORMATION_PAGE_WITH_ERRMSG, \
    SUBSCRIBE_ACTIVITY_START_NOTI_TID
from util.const.qiniu_img import CDN_QINIU_TIME_IMG, CDN_QINIU_ADDRESS_IMG, CDN_QINIU_UNKNOWN_HEAD_IMG, \
    CDN_QINIU_BOY_HEAD_IMG, CDN_QINIU_GIRL_HEAD_IMG
from util.const.response import RESP_OK, RESP_JOIN_ACTIVITY_FAILED, \
    RESP_HAS_ONGOING_ACTIVITY, \
    RESP_NEED_FILL_INFO


class GuanInfoService(BaseService):
    def __init__(self, activityId, passport):
        self.activityId = activityId
        self.passport = passport
        self.passportId = passport.get('id', 0)
        self.activityRecord = None
        self.myInformationPage = MYINFORMATION_PAGE_WITH_ERRMSG
        self.reloadActivityRecord()
        super(GuanInfoService, self).__init__()

    @lazy_property
    def addressRecord(self):
        return AddressModel.getById(self.activityRecord.address_id)

    @lazy_property
    def userRecord(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    @lazy_property
    def oppositeUserRecord(self):
        if not self.userRecord:
            return None
        elif self.userRecord.sexIndex == MODEL_SEX_MALE_INDEX:
            passportId = self.activityRecord.girl_passport_id
        else:
            passportId = self.activityRecord.boy_passport_id

        return UserModel.getByPassportId(passportId=passportId)

    @property
    def timeIcon(self):
        return CDN_QINIU_TIME_IMG

    @property
    def addressIcon(self):
        return CDN_QINIU_ADDRESS_IMG

    @property
    def oppositeImg(self):
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
        return self.addressRecord.img

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
    def oppositeDataPairs(self):
        if not self.oppositeUserRecord:
            return []

        checkDynamicData = False
        uh = UserHelper(self.oppositeUserRecord)
        informationList = uh.getInformationList(checkDynamicData)
        opTypeMapInformation = {i.bindChange: i for i in informationList}
        pairs = []
        for opTypes in uh.getInformationPariList():
            pair = []
            for opType in opTypes:
                if opType not in opTypeMapInformation:
                    continue
                information = opTypeMapInformation[opType]
                pair.append({
                    "desc": information.desc + ":",
                    "subDesc": information.subDesc,
                    "value": information.fullValue,
                })
            pairs.append(pair)

        return pairs

    def getMeetResult(self):
        if self.passportId == self.activityRecord.boy_passport_id:
            meet_result = self.activityRecord.boy_meet_result
        elif self.passportId == self.activityRecord.girl_passport_id:
            meet_result = self.activityRecord.girl_meet_result
        else:
            meet_result = 0
        return {
            "value": MODEL_MEET_RESULT_MAP[meet_result],
            "selectValueIndex": meet_result,
            "choiceList": MODEL_MEET_RESULT_CHOICE_LIST,
        }
    
    def getGuanInfo(self):
        subscribeTemplateIds = [SUBSCRIBE_ACTIVITY_START_NOTI_TID]  # 尽最大可能搜集订阅消息
        return {
            "guanId": self.activityId,
            "activity": {
                "img": self.img,
                "time": self.time,
                "address": self.address,
            },
            "opposite": {  # 发邀请的对象信息
                "oppositeImg": self.oppositeImg,
                "oppositeDataPairs": self.oppositeDataPairs,
            },
            "operate": {  # 操作信息
                "opDesc": self.opDesc,
                "opType": self.opType,
                "isAfterMeet": int(self.activityRecord.start_time < datetime.datetime.now()),
                "meetResultDesc": "点评内容只会被自己看到",
                "meetResult": self.getMeetResult(),
                "subscribeTemplateIds": subscribeTemplateIds,
                "myRequirementPage": MYREQUIREMENT_PAGE,
                "myInformationPage": self.myInformationPage,
                "requirementResult": "%d人满足期望" % UserModel.getMatchCnt(passportId=self.passportId)
            },
        }

    def reloadActivityRecord(self):
        self.activityRecord = ActivityModel.getById(self.activityId)

    @property
    def hasOngoingActivity(self):
        return bool(ActivityModel.getOngoingActivity(self.passportId))

    def getRequirement(self):
        if self.opType == GUAN_INFO_OP_TYPE_INVITE:
            return None
        elif self.opType == GUAN_INFO_OP_TYPE_JOIN:
            if self.userRecord.sex == MODEL_SEX_MALE_INDEX and self.activityRecord.boy_passport_id != 0:  # 加入了
                return UNREACHABLE_REQUIREMENT
            if self.userRecord.sex == MODEL_SEX_FEMALE_INDEX and self.activityRecord.girl_passport_id != 0:  # 加不了
                return UNREACHABLE_REQUIREMENT
            invitePid = self.activityRecord.girl_passport_id if self.userRecord.sex == MODEL_SEX_MALE_INDEX else self.activityRecord.boy_passport_id
            if not invitePid:  # 有问题的活动
                return UNREACHABLE_REQUIREMENT
            return RequirementModel.getByPassportId(invitePid)
        elif self.opType == GUAN_INFO_OP_TYPE_QUIT:
            if self.activityRecord.boy_passport_id != 0 and self.activityRecord.girl_passport_id != 0:  # 退前，男女都已就位
                return UNREACHABLE_REQUIREMENT
            invitePid = 0
            if self.userRecord.sex == MODEL_SEX_MALE_INDEX:
                if self.activityRecord.boy_passport_id != 0:  # 退前
                    invitePid = self.activityRecord.boy_passport_id
                elif self.activityRecord.girl_passport_id != 0:  # 退后的活动，人不空
                    invitePid = self.activityRecord.girl_passport_id
            elif self.userRecord.sex == MODEL_SEX_FEMALE_INDEX:
                if self.activityRecord.girl_passport_id != 0:  # 退前
                    invitePid = self.activityRecord.girl_passport_id
                elif self.activityRecord.boy_passport_id != 0:  # 退后的活动，人不空
                    invitePid = self.activityRecord.boy_passport_id
            if not invitePid:  # 有问题的活动
                return UNREACHABLE_REQUIREMENT
            return RequirementModel.getByPassportId(invitePid)
        return UNREACHABLE_REQUIREMENT  # 有问题


    def parseUpdataParams(self, opType, sexIndex):
        updateParams = {}
        whereParams = []
        if opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN]:
            passportId = self.passportId
            if self.activityRecord.state == MODEL_ACTIVITY_STATE_EMPTY:
                updateParams['state'] = MODEL_ACTIVITY_STATE_INVITING
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_EMPTY)
            elif self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITING:
                updateParams['state'] = MODEL_ACTIVITY_STATE_INVITE_SUCCESS
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_INVITING)
        else:
            passportId = 0
            if self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITING:
                updateParams['state'] = MODEL_ACTIVITY_STATE_EMPTY
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_INVITING)
            elif self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
                updateParams['state'] = MODEL_ACTIVITY_STATE_INVITING
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS)
        if sexIndex == MODEL_SEX_MALE_INDEX:
            updateParams['boy_passport_id'] = passportId
        elif sexIndex == MODEL_SEX_FEMALE_INDEX:
            updateParams['girl_passport_id'] = passportId
        return updateParams, whereParams

    def updateMyInformationPage(self, ret):
        if ret['code'] == RESP_NEED_FILL_INFO['code']:
            self.myInformationPage = self.myInformationPage + ret['errMsg']

    @lock("activityOprete:{activityId}", failRet=RESP_JOIN_ACTIVITY_FAILED)  # 加一个分布式锁
    def activityOprete(self, opType):
        """对活动进行操作"""
        # 参加前检查
        uis = UserInfoService(self.passport)
        needFilled = uis.userInfoNeedFilled()  # 个人信息完善程度检查不通过
        if needFilled:
            return needFilled
        if self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
            return RESP_JOIN_ACTIVITY_FAILED
        if opType != self.opType:
            return RESP_JOIN_ACTIVITY_FAILED
        if self.hasOngoingActivity and \
                opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN]:  # 有进行中的活动，不能再次参与
            return RESP_HAS_ONGOING_ACTIVITY
        requirement = self.getRequirement()
        if self.opType == GUAN_INFO_OP_TYPE_JOIN and not MatchHelper.match(self.userRecord, requirement):
            return RESP_JOIN_ACTIVITY_FAILED
        # todo 这个开关，前期可以不开。因为让用户帮我们拉新，是需要一定的吸引力和号召力的，前期不行。前期还得需要我们主动去推广，去营销，不得偷懒。
        # if opType == GUAN_INFO_OP_TYPE_JOIN and not ShareModel.getAcceptCnt(self.passportId):
        #     return RESP_NEED_INVITE_OR_MEMBER
        # 操作执行结果入库
        updateParams, whereParams = self.parseUpdataParams(opType, uis.userInfo.sexIndex)
        ret = ActivityModel.updateById(self.activityId, *whereParams, **updateParams)
        if not ret:
            return RESP_JOIN_ACTIVITY_FAILED
        ActivityChangeRecordModel.addOne(self.activityId, self.passportId, opType)
        # 重载一下活动信息
        self.reloadActivityRecord()
        # 更新活动id匹配缓存
        changeByRequirement(self.activityRecord.id, requirement, self.getRequirement())
        return RESP_OK  # todo 可以根据不同的场景，可以返回 RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI
