#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""注册时绑定手机号。明文只进加密库，不写通行证上的 phone 列。"""
import logging

from model.sensitive_record import SensitiveRecordModel
from service.common.phone_number import mainland_mobile
from service.sensitive.vault import SensitiveVault
from util.const.identity import KIND_PHONE, PHONE_CONTENT_TYPE
from util.wx_phone import phone_info

logger = logging.getLogger(__name__)


class PhoneBindService(object):

    def bind(self, passport_id, phone_code):
        number = mainland_mobile(phone_info(phone_code))
        if not number:
            logger.info("手机号未绑定 passport=%s", passport_id)
            return False
        row_id = SensitiveVault().store(
            passport_id,
            KIND_PHONE,
            number.encode('utf-8'),
            PHONE_CONTENT_TYPE,
        )
        return bool(row_id)

    def bound(self, passport_id):
        if not passport_id:
            return False
        return SensitiveRecordModel.latest(passport_id, KIND_PHONE) is not None
