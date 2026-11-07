#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.passport import PassportModel
from model.share import ShareModel
from ral.passport import putSession
from service import BaseService
from service.identity.runtime_key import put_unionid
from service.phone_bind import PhoneBindService
from service.sensitive.legacy_seal import seal_passport_plaintext
from util.const.identity import PROVIDER_WECHAT
from util.encode import generate_access_token
from util.sensitive_cipher import union_lookup

logger = logging.getLogger(__name__)


class LoginService(BaseService):

    def login(self, assertion, share_passport_id):
        """登录只把通行证放进会话。真实 unionid 只进 Redis，库里只留查找值。"""
        passport = self._passport_for(assertion, share_passport_id)
        if not passport:
            return None
        seal_passport_plaintext(passport.id, assertion.secret_material)
        if not put_unionid(passport.id, assertion.secret_material):
            return None
        logger.info(
            "登录完成，身份查找值已落在通行证上 passport=%s provider=%s",
            passport.id,
            assertion.provider,
        )
        access_token = generate_access_token(passport.id)
        sign_secret = putSession(access_token, passport.id)
        openid = assertion.account_key if assertion.provider == PROVIDER_WECHAT else ''
        phone_bound = PhoneBindService().bound(passport.id)
        return access_token, sign_secret, openid, phone_bound, passport.id

    def _passport_for(self, assertion, share_passport_id):
        material = assertion.secret_material
        if not material:
            logger.info("身份提供方没有密钥材料 provider=%s", assertion.provider)
            return None
        union_key = union_lookup(material)
        passport = PassportModel.get_by_union_key(union_key)
        if passport:
            return passport
        passport = PassportModel.add_with_union_key(union_key)
        if passport:
            self._bind_share(share_passport_id, passport.id)
        return passport

    def _bind_share(self, share_passport_id, passport_id):
        sharer_id = int(share_passport_id or 0)
        if sharer_id <= 0 or sharer_id == passport_id:
            return
        if not PassportModel.getById(sharer_id):
            logger.info("分享人通行证不存在 sharer=%s", sharer_id)
            return
        ShareModel.addOne(sharer_id, passport_id)
        logger.info("已记下分享 sharer=%s accept=%s", sharer_id, passport_id)
