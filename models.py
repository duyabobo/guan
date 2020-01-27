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
    guan_type = Column(Integer)  # 问答类型
    guan_point = Column(Integer)  # 积分
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class GuanInfo(Base):
    """关关问题数据表"""
    __tablename__ = 'guan_info'
    id = Column(Integer, primary_key=True)  # 自增
    guan_id = Column(Integer)  # guanguan id
    question = Column(String)  # 问题内容
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class Answers(Base):
    """关关答案数据表"""
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)  # 自增
    guan_info_id = Column(Integer)  # guan info id
    answer_key = Column(String)  # 展示的答案内容
    answer_evaluation = Column(String)  # 问答对应的测评内容
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class GuanAnswers(Base):
    """关关回答数据表"""
    __tablename__ = 'guan_answers'
    id = Column(Integer, primary_key=True)  # 自增
    guan_info_id = Column(Integer)  # guan info id
    user_id = Column(Integer)  # user_id
    answer_id = Column(Integer)  # Answers id
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
