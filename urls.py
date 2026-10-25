#!/usr/bin/env python
# coding=utf-8
from handler import public
from handler.miniprogram import guan_info, guanguan, subscribe
from handler.user import login, match_config, phone
from service.common.phone_number import PHONE_BIND_PATH, PHONE_CODE_PATH

handlers = [
    # 公开入口：不走签名校验
    (r'/$', public.LandingHandler),
    (r'/index$', public.LandingHandler),
    (r'/health$', public.HealthHandler),
    # 小程序接口：统一走 BaseHandler 的签名、限频和防重放
    (r'/login$', login.LoginHandler),
    (PHONE_CODE_PATH + '$', phone.PhoneCodeHandler),
    (PHONE_BIND_PATH + '$', phone.PhoneHandler),
    (r'/guanguan$', guanguan.GuanguanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/meet_result$', guan_info.MeetResultHandler),
    (r'/match_config$', match_config.MatchConfigHandler),
    (r'/voice_text$', match_config.VoiceTextHandler),
    (r'/subscribe_cb$', subscribe.SubscribeCBHandler),
]
