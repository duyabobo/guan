#! /usr/bin/env python
# -*- coding: utf-8 -*-
import gevent

from model.verify import VerifyModel
from service import BaseService
from service.myself import UserInfoService
from util.class_helper import lazy_property
from util.const.match import OP_TYPE_VERIFY
from util.const.response import RESP_HAS_EMAIL_VERIFY_RECENTLY, RESP_OK, \
    RESP_HAS_EMAIL_VERIFY_FAILED, RESP_HAS_EMAIL_IS_NOT_COMPANY, RESP_HAS_SEND_EMAIL, RESP_EMAIL_IS_NOT_VALID
from util.encryption import getEncryptMail
from util.mail import send_email_verify
from util.redis_conn import redisConn
from util.verify import generate_code
import re

EMAIL_VERIFY_RECORD = "email_verify_record:{passportId}"
EMAIL_VERIFY_CODE = "email_verify_code:{passportId}:{email}"


class EmailVerifyService(BaseService):

    def __init__(self, currentPassport):
        self.currentPassport = currentPassport
        self.passportId = currentPassport.get('id', 0)
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

    def setCodeToCache(self, encryptedMail, code):
        redisConn.set(self.getVerifyCodeKey(encryptedMail), code, ex=5*60)

    def checkCodeWithCache(self, openid, email, code):
        encryptedMail = getEncryptMail(openid, email)
        if redisConn.get(self.getVerifyCodeKey(encryptedMail)) != code:
            return RESP_HAS_EMAIL_VERIFY_FAILED
        mailType = VerifyModel.getMailType(email)
        VerifyModel.updateVerifyStatus(passportId=self.passportId, encryptedMail=encryptedMail, mailType=mailType)
        UserInfoService(self.currentPassport).updateMyselfInfo(OP_TYPE_VERIFY, mailType)
        self.recordVerifyOperate()
        return RESP_OK

    def emailIsCompany(self, email):
        return True  # todo 可以不断累积白名单，暂时全部放开

    def hasSendEmailRecently(self, email):
        if redisConn.get(self.getVerifyCodeKey(email)):
            return True
        return False

    def emailIsValid(self, email):
        regex = re.compile(r'([A-Za-z0-9] + [.-_]) * [A-Za-z0-9] + @[A-Za-z0-9 -] + (\.[A-Z|a-z]{2, }) +')
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def sendVerifyEmail(self, openid, email):
        if not self.emailIsCompany(email):
            return RESP_HAS_EMAIL_IS_NOT_COMPANY
        if self.hasVerifiedRecently:
            return RESP_HAS_EMAIL_VERIFY_RECENTLY
        if self.hasSendEmailRecently(email):
            return RESP_HAS_SEND_EMAIL
        if self.emailIsValid(email):
            return RESP_EMAIL_IS_NOT_VALID

        code = generate_code()
        # 加密缓存code
        encryptedMail = getEncryptMail(openid, email)
        self.setCodeToCache(encryptedMail, code)
        # 可以用celery替代
        gevent.spawn(send_email_verify, email, code)

        return RESP_OK
