#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import os
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.web

import util.config
from urls import handlers
from util.database import engine

reload(sys)
sys.setdefaultencoding('utf-8')


def main():
    port = util.config.get('global', 'port')
    server = util.config.get('global', 'server')
    debug = util.config.get('global', 'debug')
    cookie_secret = util.config.get('global', 'cookie_secret')

    application = tornado.web.Application(handlers, **{
        'debug': True if debug == 'true' else False,
        'cookie_secret': cookie_secret,
        'template_path': 'template',
        'static_path': 'static',
    })

    application.engine = engine
    http_server = tornado.httpserver.HTTPServer(
        application,
        ssl_options={
            "certfile": '/home/guan/service.pem',
            "keyfile": '/home/guan/service.key',
        }
    ) if server == 'online' else tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    print ('>>>>> Starting development server at http://localhost:{}/ <<<<<'.format(port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
