#! /usr/bin/env python
# -*- coding: utf-8 -*-
import gevent

from model.verify import VerifyModel
from service import BaseService
from util.class_helper import lazy_property
from util.const.match import MODEL_MAIL_VERIFY_STATUS_NO
from util.const.response import RESP_HAS_EMAIL_VERIFY_RECENTLY, RESP_OK, \
    RESP_HAS_EMAIL_VERIFY_FAILED, RESP_HAS_EMAIL_IS_NOT_COMPANY, RESP_HAS_SEND_EMAIL
from util.mail import send_email_verify
from util.redis_conn import redisConn
from util.verify import generate_code

EMAIL_VERIFY_RECORD = "email_verify_record:{passportId}"
EMAIL_VERIFY_CODE = "email_verify_code:{passportId}:{email}"


class EmailVerifyService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        super(EmailVerifyService, self).__init__()
        self.verifyRecordKey = EMAIL_VERIFY_RECORD.format(passportId=self.passportId)

    @property
    def hasVerifiedRecently(self):
        return bool(redisConn.get(self.verifyRecordKey))

    @lazy_property
    def verifyRecord(self):
        return VerifyModel.getByPassportId(self.passportId)

    def recordVerifyOperate(self):
        redisConn.set(self.verifyRecordKey, 1, ex=6*30*24*3600)

    def getVerifyCodeKey(self, email):
        return EMAIL_VERIFY_CODE.format(passportId=self.passportId, email=email)

    def setCodeToCache(self, email, code):
        redisConn.set(self.getVerifyCodeKey(email), code, ex=5*60)

    def checkCodeWithCache(self, email, code):
        if redisConn.get(self.getVerifyCodeKey(email)) != code:
            return RESP_HAS_EMAIL_VERIFY_FAILED
        VerifyModel.updateVerifyStatus(self.passportId, email)
        self.recordVerifyOperate()
        return RESP_OK

    def emailIsCompany(self, email):
        return True  # todo 可以不断累积白名单，暂时全部放开

    def hasSendEmailRecently(self, email):
        if redisConn.get(self.getVerifyCodeKey(email)):
            return True
        return False

    def sendVerifyEmail(self, email):
        if not self.emailIsCompany(email):
            return RESP_HAS_EMAIL_IS_NOT_COMPANY
        if self.hasVerifiedRecently:
            return RESP_HAS_EMAIL_VERIFY_RECENTLY
        if self.hasSendEmailRecently(email):
            return RESP_HAS_SEND_EMAIL
        if self.verifyRecord.mail != email and self.verifyRecord.mail_verify_status == MODEL_MAIL_VERIFY_STATUS_NO:
            VerifyModel.fillWorkMail(self.passportId, email)
        code = generate_code()
        # 可以用celery替代
        gevent.spawn(send_email_verify, email, code)
        self.setCodeToCache(email, code)
        return RESP_OK
