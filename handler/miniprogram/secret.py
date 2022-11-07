#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor, Response


class SecretHandler(BaseHandler):
    @superMonitor
    def get(self):
        return Response(data={
            "title": "",
            "descList": [
                "根据法律规定，开发者仅处理实现小程序功能所必要的如下信息：",
                "1，为了根据地理位置推荐活动，开发者将在获取你的明示同意后，收集你的位置信息。",
                "2，为了用户自拍照生成头像，开发者将在获取你的明示同意后，访问你的摄像头。",
                "3，为了根据信息和期望匹配见面对象，开发者将在应用里引导你完善个人信息，以及个人期望。",
                "开发者承诺: ",
                "1，除上面两个目的之外，您的信息不会被用于他处。",
                "2，您的信息不会被泄漏，不会被盗用，不会被篡改。",
            ]
        })
