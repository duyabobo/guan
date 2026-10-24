#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""短信验证码通过后绑定手机号。明文只进加密库。"""
import logging

from model.sensitive_record import SensitiveRecordModel
from service.phone_code import PhoneCodeService
from service.sensitive.vault import SensitiveVault
from util.const.identity import KIND_PHONE, PHONE_CONTENT_TYPE

logger = logging.getLogger(__name__)


class PhoneBindService(object):

    def bind(self, passport_id, raw_phone, raw_code):
        number = PhoneCodeService().take(passport_id, raw_phone, raw_code)
        if not number:
            return False
        row_id = SensitiveVault().store(
            passport_id,
            KIND_PHONE,
            number.encode('utf-8'),
            PHONE_CONTENT_TYPE,
        )
        if not row_id:
            logger.info("手机号未写入 passport=%s", passport_id)
        return bool(row_id)

    def bound(self, passport_id):
        if not passport_id:
            return False
        return SensitiveRecordModel.latest(passport_id, KIND_PHONE) is not None
