#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GuanType(Base):
    """关关类型"""
    __tablename__ = 'guan_type'
    id = Column(Integer, primary_key=True)  # 自增
    name = Column(String)  # 问答名字
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class GuanGuan(Base):
    """关关问答封面数据"""
    __tablename__ = 'guanguan'
    id = Column(Integer, primary_key=True)  # 自增
    name = Column(String)  # 问答名字
    guan_type_id = Column(Integer)  # 问答类型
    guan_point = Column(Integer)  # 积分
    status = Column(Integer)  # 状态
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


class AnswerInfo(Base):
    """关关答案数据表"""
    __tablename__ = 'answer_info'
    id = Column(Integer, primary_key=True)  # 自增
    guan_id = Column(Integer)  # guanguan id
    guan_info_id = Column(Integer)  # guan info id
    answer_key = Column(String)  # 展示的答案内容
    answer_evaluation = Column(String)  # 问答对应的测评内容
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class GuanAnswer(Base):
    """关关回答数据表"""
    __tablename__ = 'guan_answer'
    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer)  # user_id
    guan_id = Column(Integer)  # guanguan id
    guan_info_id = Column(Integer)  # guan_info id
    answer_info_id = Column(Integer)  # answer_info id
    guan_answer_status = Column(Integer, default=1)  # 回答数据的状态：1 正常，0 已删除
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class GuanPoint(Base):
    """关关积分详情表"""
    __tablename__ = 'guan_point'
    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer)  # user_id
    guan_id = Column(Integer)  # guanguan id
    guan_point = Column(Integer)  # 积分数
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class User(Base):
    """用户基础数据"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)  # 自增
    mobile = Column(String)  # 手机号，也就是账号，数据库中存储的是加密数据  -- index --
    openid = Column(String)  # 微信 openid
    password = Column(String)  # 密码，md5加密后存储  -- index --
    user_status = Column(Integer, default=0)  # 用户状态：见 USER_STATUS  -- index --
    guan_point = Column(Integer, default=0)  # 积分
    nickname = Column(String, default='')  # 昵称
    profile_photo = Column(String, default='')  # 头像url
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class Suggestion(Base):
    """用户意见"""
    __tablename__ = 'suggestion'
    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer)  # user_id
    suggestion_content = Column(Integer)  # 意见内容
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class OfflineMeeting(Base):
    """线下见面活动数据"""
    __tablename__ = 'offline_meeting'
    id = Column(Integer, primary_key=True)  # 自增
    guan_id = Column(Integer)  # guan id
    time = Column(TIMESTAMP)  # 时间
    address = Column(String)  # 地址
    latitude = Column(Float)  # 纬度
    longitude = Column(Float)  # 经度
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间
