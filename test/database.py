#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine

from util.config import Configuration

config = Configuration(config_file="../du.conf")
username = config.get("mysql", "username")
password = config.get("mysql", "password")
host = config.get("mysql", "host")
port = config.get("mysql", "port")
database = config.get("mysql", "database")
engine = create_engine('mysql+pymysql://%s:%s@%s/%s?charset=utf8' %
                       (username, password, host, database),
                       encoding='utf-8', echo=False, pool_size=50, max_overflow=0, pool_recycle=60)