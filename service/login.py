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
        passport = PassportModel.getByOpenid(self.dbSession, openid)
        if not passport:
            passport = PassportModel.addByOpenid(self.dbSession, openid)
            UserModel.addByPassportId(self.dbSession, passport.id)
            RequirementModel.addByPassportId(self.dbSession, passport.id)
            VerifyModel.addByPassportId(self.dbSession, passport.id)

        accessToken = generate_access_token(passport.id)
        currentUserInfoJson = putSession(self.redis, accessToken, passport)
        return accessToken, currentUserInfoJson
