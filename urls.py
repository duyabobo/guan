#!/usr/bin/env python
# coding=utf-8
from handler.miniprogram import guan_info, guanguan, subscribe
from handler.pc import index
from handler.user import login, match_config
from handler import example

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/index$', index.IndexHandler),
    (r'/login$', login.LoginHandler),
    (r'/guanguan$', guanguan.GuanguanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/meet_result$', guan_info.MeetResultHandler),
    (r'/match_config$', match_config.MatchConfigHandler),
    (r'/voice_text$', match_config.VoiceTextHandler),
    (r'/subscribe_cb$', subscribe.SubscribeCBHandler),
]
