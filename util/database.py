#!/usr/bin/python
# -*- coding=utf-8 -*-
import util.config
from redis import StrictRedis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

username = util.config.get("mysql", "username")
password = util.config.get("mysql", "password")
host = util.config.get("mysql", "host")
port = util.config.get("mysql", "port")
database = util.config.get("mysql", "database")
engine = create_engine('mysql://%s:%s@%s:%s/%s?charset=utf8' %
                       (username, password, host, port, database),
                       encoding='utf-8', echo=False, pool_size=50, max_overflow=0, pool_recycle=60)

engine_offline = create_engine('mysql://%s:%s@%s:%s/%s?charset=utf8' %
                               (username, password, host, port, database),
                               encoding='utf-8', echo=False, max_overflow=0, pool_recycle=60)
mysql_offline_session = sessionmaker(bind=engine_offline)()

redis_offline_session = StrictRedis(util.config.get('redis', 'host'),
                                    util.config.get('redis', 'port'))
