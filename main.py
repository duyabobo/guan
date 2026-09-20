#!/usr/bin/env python
# coding=utf-8
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web
from gevent import monkey

import util.config
from urls import handlers
from util.database import engine

# tornado 支持 https，如果要使用 gevent，需要 patch_all 的时候，把 ssl 设置为 False
monkey.patch_all(ssl=False, thread=False, socket=False)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)


def _build_ssl_options():
    return {
        "certfile": '/home/guan/service.pem',
        "keyfile": '/home/guan/service.key',
    }


def main():
    port = util.config.get('global', 'port')
    server = util.config.get('global', 'server')
    debug = util.config.get('global', 'debug')
    cookie_secret = util.config.get('global', 'cookie_secret')

    application = tornado.web.Application(handlers, **{
        'debug': debug == 'true',
        'cookie_secret': cookie_secret,
        'template_path': 'handler/template',
        'static_path': 'handler/static',
    })

    application.engine = engine

    is_online = server == 'online'
    http_server = (
        tornado.httpserver.HTTPServer(application, ssl_options=_build_ssl_options())
        if is_online
        else tornado.httpserver.HTTPServer(application)
    )
    http_server.listen(port)
    logger.info("Starting server at http://localhost:%s/ (mode=%s, debug=%s)", port, server, debug)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
