#!/usr/bin/python
# -*- coding=utf-8 -*-
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_CERT_FILE = '/home/guan/service.pem'
DEFAULT_KEY_FILE = '/home/guan/service.key'

# 不用 OpenSSL 的 SSL_CERT_FILE：那个是出站校验证书包，会把服务端证书误当成 CA。
CERT_ENV = 'GUAN_HTTPS_CERT_FILE'
KEY_ENV = 'GUAN_HTTPS_KEY_FILE'


def build_ssl_options():
    certfile = os.environ.get(CERT_ENV) or DEFAULT_CERT_FILE
    keyfile = os.environ.get(KEY_ENV) or DEFAULT_KEY_FILE
    missing = [path for path in (certfile, keyfile) if _unusable(path)]
    if missing:
        logger.error("HTTPS 证书不存在或为空: %s", ', '.join(missing))
        raise FileNotFoundError('HTTPS 证书不存在或为空: %s' % ', '.join(missing))
    logger.info("HTTPS 证书 %s", certfile)
    return {'certfile': certfile, 'keyfile': keyfile}


def _unusable(path):
    return not os.path.isfile(path) or os.path.getsize(path) == 0
