#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""微信手机号组件返回的大陆手机号。只做格式判断，不落库。"""

PHONE_COUNTRY_CN = '86'
PHONE_DIGIT_COUNT = 11


def mainland_mobile(phone_info):
    if not isinstance(phone_info, dict):
        return ''
    country = str(phone_info.get('countryCode') or '')
    number = str(phone_info.get('purePhoneNumber') or '').strip()
    if country != PHONE_COUNTRY_CN:
        return ''
    if len(number) != PHONE_DIGIT_COUNT or not number.isdigit():
        return ''
    return number
