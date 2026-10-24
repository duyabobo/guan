#!/usr/bin/env python
# coding=utf-8
from handler.miniprogram import guan_info, guanguan, pay_notify, subscribe
from handler.pc import index
from handler.user import login, match_config, phone
from handler import example

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/index$', index.IndexHandler),
    (r'/login$', login.LoginHandler),
    (r'/phone$', phone.PhoneHandler),
    (r'/guanguan$', guanguan.GuanguanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/meet_result$', guan_info.MeetResultHandler),
    (r'/match_config$', match_config.MatchConfigHandler),
    (r'/voice_text$', match_config.VoiceTextHandler),
    (r'/subscribe_cb$', subscribe.SubscribeCBHandler),
    (r'/wx_pay_notify$', pay_notify.WxPayNotifyHandler),
]
