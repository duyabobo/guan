#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.passport import PassportModel
from model.requirement import RequirementModel
from model.share import ShareModel
from model.user import UserModel
from model.verify import VerifyModel
from ral.passport import putSession
from service import BaseService
from util.encode import generate_access_token


class LoginService(BaseService):

    def login(self, openid, shareOpenid):
        """检查用户记录，如果不存在就新增，并对该用户创建session"""
        passport = PassportModel.getByOpenid(openid)
        if not passport:
            passport = PassportModel.addByOpenid(openid)
            UserModel.addByPassportId(passport.id)
            RequirementModel.addByPassportId(passport.id)
            VerifyModel.addByPassportId(passport.id)
            # shareOpenid 的生命周期是：
            # 1, 分享者分享首页时带上当前用户的openid（为啥不是passportId呢？其实也行，但是客户端有token，就用不到passportId作为参数了）作为shareOpenid
            # 2, 领取者打开首页会在小程序本地保存这个shareOpenid
            # 3, 领取者登录时会把本地保存的shareOpenid作为参数带过来
            # 4, 后端登录接口就在这里接收到 shareOpenid
            if shareOpenid and openid != shareOpenid:
                sharePassport = PassportModel.getByOpenid(shareOpenid)
                if sharePassport:
                    ShareModel.addOne(sharePassport.id, passport.id)

        accessToken = generate_access_token(passport.id)
        secret = putSession(accessToken, passport.id)
        return accessToken, secret
