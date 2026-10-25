#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""线上启动前的配置体检。发现还在用示例口令或缺关键密钥，直接拒绝启动，而不是带着弱口令上线。"""
import logging

import util.config

logger = logging.getLogger(__name__)

# docker-compose、entrypoint、.env.example 里出现过的示例口令
WEAK_SECRETS = frozenset({'', 'change_me_in_production', 'guan123', 'root123', 'your_wx_secret'})


def find_config_problems():
    """返回配置问题列表。日志和异常里只写配置项名，不写取值。"""
    problems = []
    if util.config.get_optional('mysql', 'password') in WEAK_SECRETS:
        problems.append('mysql.password 为空或仍是示例口令')
    if util.config.get_optional('redis', 'password') in WEAK_SECRETS:
        problems.append('redis.password 为空：Redis 里存着运行时身份密钥，必须设置密码')
    if util.config.get_optional('weixin', 'secret') in WEAK_SECRETS:
        problems.append('weixin.secret 为空：登录和见面盲索引都依赖它')
    return problems


def assert_online_config_safe():
    problems = find_config_problems()
    if not problems:
        logger.info("线上配置体检通过")
        return
    for problem in problems:
        logger.error("线上配置体检未通过: %s", problem)
    raise SystemExit('线上配置体检未通过，共 %d 项，拒绝启动' % len(problems))
