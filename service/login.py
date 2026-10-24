#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.identity_secret import IdentitySecretModel
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

    def login(self, assertion, share_openid):
        """登录只把通行证放进会话。真实 unionid 只进 Redis，库里只留自加密封存。"""
        passport = self._passport_for(assertion, share_openid)
        if not IdentitySecretModel.accepts(passport.id, assertion.provider, assertion.secret_material):
            return None
        seal_passport_plaintext(passport.id, assertion.secret_material)
        if not IdentitySecretModel.save_sealed(passport.id, assertion.provider, assertion.secret_material):
            return None
        if not put_unionid(passport.id, assertion.secret_material):
            return None
        logger.info(
            "登录完成，身份密钥已封存，明文只在运行时 passport=%s provider=%s",
            passport.id,
            assertion.provider,
        )
        access_token = generate_access_token(passport.id)
        sign_secret = putSession(access_token, passport.id)
        openid = assertion.account_key if assertion.provider == PROVIDER_WECHAT else ''
        phone_bound = PhoneBindService().bound(passport.id)
        return access_token, sign_secret, openid, phone_bound

    def _passport_for(self, assertion, share_openid):
        if assertion.provider == PROVIDER_WECHAT:
            return self._wechat_passport(assertion.account_key, share_openid)
        return self._bound_passport(assertion)

    def _wechat_passport(self, openid, share_openid):
        passport = PassportModel.getByOpenid(openid)
        if passport:
            return passport
        passport = self._create_passport(openid)
        self._bind_share(openid, share_openid, passport.id)
        return passport

    def _bound_passport(self, assertion):
        if not assertion.secret_material:
            logger.info("身份提供方没有密钥材料 provider=%s", assertion.provider)
            return self._create_passport('')
        account_key = union_lookup(assertion.secret_material)
        passport_id = IdentitySecretModel.passport_id_of(assertion.provider, account_key)
        if passport_id:
            passport = PassportModel.getById(passport_id)
            if passport:
                return passport
        logger.info("身份提供方首次登录，创建通行证 provider=%s", assertion.provider)
        return self._create_passport('')

    def _create_passport(self, openid):
        if openid:
            return PassportModel.addByOpenid(openid)
        return PassportModel.addBare()

    def _bind_share(self, openid, share_openid, passport_id):
        # 分享者把 openid 放进分享链接，领取者登录时带上，用来记一次分享关系。
        if not share_openid or openid == share_openid:
            return
        share_passport = PassportModel.getByOpenid(share_openid)
        if share_passport:
            ShareModel.addOne(share_passport.id, passport_id)
