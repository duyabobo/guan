#!/usr/bin/python
# -*- coding=utf-8 -*-
import util.config
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

DB_DRIVER = 'mysql+pymysql'
DB_CHARSET = 'utf8mb4'  # utf8 在 MySQL 里只有 3 字节，存不下 emoji
DB_POOL_SIZE = 50
DB_POOL_RECYCLE_SEC = 1800  # 小于 MySQL 的 wait_timeout；连接是否已失效由 pool_pre_ping 兜底
DB_POOL_TIMEOUT_SEC = 10  # 池满时最多等多久拿连接，等不到就报错，不无限排队
DB_CONNECT_TIMEOUT_SEC = 5
DB_READ_WRITE_TIMEOUT_SEC = 30


def _build_url():
    """用 URL.create 拼连接串，用户名密码里的特殊字符会被正确转义。"""
    return URL.create(
        DB_DRIVER,
        username=util.config.get("mysql", "username"),
        password=util.config.get("mysql", "password"),
        host=util.config.get("mysql", "host"),
        port=int(util.config.get("mysql", "port")),
        database=util.config.get("mysql", "database"),
        query={'charset': DB_CHARSET},
    )


engine = create_engine(
    _build_url(),
    echo=False,
    pool_size=DB_POOL_SIZE,
    max_overflow=0,
    pool_recycle=DB_POOL_RECYCLE_SEC,
    pool_pre_ping=True,
    pool_timeout=DB_POOL_TIMEOUT_SEC,
    connect_args={
        'connect_timeout': DB_CONNECT_TIMEOUT_SEC,
        'read_timeout': DB_READ_WRITE_TIMEOUT_SEC,
        'write_timeout': DB_READ_WRITE_TIMEOUT_SEC,
    },
)

# 每个请求（或每个后台任务）从这里拿自己的 Session，不共享
SessionFactory = sessionmaker(bind=engine)
