#! /usr/bin/env python
# -*- coding: utf-8 -*-


class IdentityAssertion(object):
    """一次登录核验的结果。secret_material 只用于落库和加密，不进入会话。"""

    def __init__(self, provider, account_key, secret_material):
        self.provider = provider
        self.account_key = account_key
        self.secret_material = secret_material

    def __repr__(self):
        return 'IdentityAssertion(provider=%s)' % (self.provider,)
