#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.passport import PassportModel
from model.requirement import RequirementModel
from model.user import UserModel
from model.verify import VerifyModel
from ral.passport import putSession
from service import BaseService
from util.encode import generate_access_token


class LoginService(BaseService):

    def login(self, openid):
        """检查用户记录，如果不存在就新增，并对该用户创建session"""
        passport = PassportModel.getByOpenid(openid)
        if not passport:
            passport = PassportModel.addByOpenid(openid)
            UserModel.addByPassportId(passport.id)
            RequirementModel.addByPassportId(passport.id)
            VerifyModel.addByPassportId(passport.id)

        accessToken = generate_access_token(passport.id)
        secret = putSession(accessToken)
        return accessToken, secret
