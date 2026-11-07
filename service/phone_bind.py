#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""短信验证码通过后，把手机号用 unionid 材料加密写入通行证。"""
import logging

from model.passport import PassportModel
from service.identity.runtime_key import material_for
from service.phone_code import PhoneCodeService
from util.const.identity import PURPOSE_ENCRYPT_STORE
from util.sensitive_cipher import seal_phone

logger = logging.getLogger(__name__)


class PhoneBindService(object):

    def bind(self, passport_id, raw_phone, raw_code):
        number = PhoneCodeService().take(passport_id, raw_phone, raw_code)
        if not number:
            return False
        material = material_for(passport_id, PURPOSE_ENCRYPT_STORE)
        if not material:
            logger.info("手机号未写入，运行时没有身份密钥 passport=%s", passport_id)
            return False
        sealed = seal_phone(material, number)
        return PassportModel.save_phone(passport_id, sealed)

    def bound(self, passport_id):
        if not passport_id:
            return False
        return bool(PassportModel.phone_cipher(passport_id))
