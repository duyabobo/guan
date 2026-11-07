#!/usr/bin/python
# -*- coding=utf-8 -*-
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_CERT_FILE = '/home/guan/service.pem'
DEFAULT_KEY_FILE = '/home/guan/service.key'


def build_ssl_options():
    certfile = os.environ.get('SSL_CERT_FILE') or DEFAULT_CERT_FILE
    keyfile = os.environ.get('SSL_KEY_FILE') or DEFAULT_KEY_FILE
    missing = [path for path in (certfile, keyfile) if _unusable(path)]
    if missing:
        logger.error("HTTPS 证书不存在或为空: %s", ', '.join(missing))
        raise FileNotFoundError('HTTPS 证书不存在或为空: %s' % ', '.join(missing))
    logger.info("HTTPS 证书 %s", certfile)
    return {'certfile': certfile, 'keyfile': keyfile}


def _unusable(path):
    return not os.path.isfile(path) or os.path.getsize(path) == 0
