#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GuanGuan(Base):
    """关关问答封面数据"""
    __tablename__ = 'guanguan'
    id = Column(Integer, primary_key=True)  # 自增
    name = Column(String)  # 问答名字
    guan_type = Column(String)  # 问答类型
    guan_point = Column(Integer)  # 积分
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class User(Base):
    """用户基础数据，用户第一次进入产品需要完善一级(或基础)信息：昵称、头像、性别、是否是学生。
    其中昵称和头像随机自动生成（并可以自主修改），性别、是否是学生是必须自主完善的。
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)  # 自增
    mobile = Column(String)  # 手机号，也就是账号，数据库中存储的是加密数据  -- index --
    openid = Column(String)  # 微信 openid
    password = Column(String)  # 密码，md5加密后存储  -- index --
    user_status = Column(Integer, default=0)  # 用户状态：见 USER_STATUS  -- index --
    nickname = Column(String, default='')  # 昵称
    profile_photo = Column(String, default='')  # 头像url
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class UserInfo(Base):
    """用户数据，就是自身条件信息"""
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer, default=0)  # user_id -- index --
    sex = Column(Integer, default=-1)  # 性别：0FEMALE 1MALE
    year_of_birth = Column(Integer, default=1970)  # 出生年份
    height = Column(Integer, default=0)  # 身高（cm）
    degree = Column(Integer, default=0)  # 学历: 见DEGREE
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间
