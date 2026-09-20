#!/usr/bin/env python
# coding=utf-8
from handler import example
from handler.miniprogram import guan_info, guanguan, subscribe, contact, send_msg
from handler.pc import index
from handler.user import login, myself, requirement, match_config
from handler.verify import phone_verify

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/index$', index.IndexHandler),
    (r'/login$', login.LoginHandler),
    (r'/contact$', contact.ContactHandler),
    (r'/send_sms$', send_msg.SendSmsHandler),
    (r'/myself$', myself.MyselfHandler),
    (r'/requirement$', requirement.RequirementHandler),
    (r'/location_state$', myself.LocationStateHandler),
    (r'/guanguan$', guanguan.GuanguanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/meet_result$', guan_info.MeetResultHandler),
    (r'/match_config$', match_config.MatchConfigHandler),
    (r'/voice_text$', match_config.VoiceTextHandler),
    (r'/phone_verify$', phone_verify.PhoneVerifyHandler),
    (r'/subscribe_cb$', subscribe.SubscribeCBHandler),
    (r'/send_subscribe_msg$', subscribe.SendMsgHandler)
]
