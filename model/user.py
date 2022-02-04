#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """用户信息"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)  # 自增
    uid = Column(Integer)  # uid
    sex = Column(Integer)  # 性别：0未知，1男，2女
    birth_year = Column(Integer)  # 出生年份
    martial_status = Column(Integer)  # 婚姻现状：0未知，1未婚，2离异
    height = Column(String)  # 身高(厘米-厘米)
    weight = Column(String)  # 体重(公斤-公斤)
    month_pay = Column(String)  # 月收入(元-元)
    education = Column(Integer)  # 学历枚举
    status = Column(Integer, default=1)  # 逻辑删除标示: 0已删除，1有效
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间
