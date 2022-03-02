#! /usr/bin/env python
# -*- coding: utf-8 -*-
from service import BaseService
from util.const import RESP_HAS_EMAIL_VERIFY_RECENTLY, RESP_OK, \
    RESP_HAS_EMAIL_VERIFY_FAILED, RESP_HAS_EMAIL_IS_NOT_COMPANY, MODEL_WORK_VERIFY_STATUS_NO
from util.mail import send_email_verify
from util.verify import generate_code
from util.class_helper import lazy_property
from model.verify import VerifyModel

EMAIL_VERIFY_RECORD = "email_verify_record:{passportId}"
EMAIL_VERIFY_CODE = "email_verify_code:{passportId}:{email}"


class EmailVerifyService(BaseService):

    def __init__(self, dbSession, redis, passportId):
        self.dbSession = dbSession
        self.redis = redis
        self.passportId = passportId
        super(EmailVerifyService, self).__init__(dbSession, redis)
        self.verifyRecordKey = EMAIL_VERIFY_RECORD.format(passportId=self.passportId)

    @property
    def hasVerifiedRecently(self):
        return bool(self.redis.get(self.verifyRecordKey))

    @lazy_property
    def verifyRecord(self):
        return VerifyModel.getByPassportId(self.dbSession, self.passportId)

    def recordVerifyOperate(self):
        self.redis.set(self.verifyRecordKey, 1, ex=6*30*24*3600)

    def getVerifyCodeKey(self, email):
        return EMAIL_VERIFY_CODE.format(passportId=self.passportId, email=email)

    def setCodeToCache(self, email, code):
        self.redis.set(self.getVerifyCodeKey(email), code, ex=5*60)

    def checkCodeWithCache(self, email, code):
        if self.redis.get(self.getVerifyCodeKey(email)) != code:
            return RESP_HAS_EMAIL_VERIFY_FAILED
        VerifyModel.updateVerifyStatus(self.dbSession, self.passportId, email)
        self.recordVerifyOperate()
        return RESP_OK

    def emailIsCompany(self, email):
        return True  # todo 可以不断累积白名单，暂时全部放开

    def sendVerifyEmail(self, email):
        if not self.emailIsCompany(email):
            return RESP_HAS_EMAIL_IS_NOT_COMPANY
        if self.hasVerifiedRecently:
            return RESP_HAS_EMAIL_VERIFY_RECENTLY
        if self.verifyRecord.work_mail != email and self.verifyRecord.work_verify_status == MODEL_WORK_VERIFY_STATUS_NO:
            VerifyModel.fillWorkMail(self.dbSession, self.passportId, email)
        code = generate_code()
        # 可能有性能问题 todo
        send_email_verify(email, code)
        self.setCodeToCache(email, code)
        return RESP_OK
