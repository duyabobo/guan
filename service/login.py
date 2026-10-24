#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.identity_secret import IdentitySecretModel
from model.passport import PassportModel
from model.share import ShareModel
from ral.passport import putSession
from service import BaseService
from service.phone_bind import PhoneBindService
from util.const.identity import PROVIDER_WECHAT
from util.encode import generate_access_token

logger = logging.getLogger(__name__)


class LoginService(BaseService):

    def login(self, assertion, share_openid, phone_code=''):
        """登录只把通行证放进会话。身份密钥另表保存，不进入会话。"""
        passport = self._passport_for(assertion, share_openid)
        saved = IdentitySecretModel.save_material(
            passport.id,
            assertion.provider,
            assertion.account_key,
            assertion.secret_material,
        )
        if not saved:
            return None
        if phone_code:
            PhoneBindService().bind(passport.id, phone_code)
        logger.info(
            "登录完成，身份密钥已单独保存，未写入会话 passport=%s provider=%s",
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
        account_key = IdentitySecretModel.account_key_of(assertion.account_key)
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
