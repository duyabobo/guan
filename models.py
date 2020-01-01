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


# -------------------------- 华丽丽的分界线（下面是支撑体系）-------------------------------------------
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
    max_love_status = Column(Integer, default=0)  # 最新恋爱状态取值范围：0匹配中，1约会中，2恋爱中  -- index --
    nickname = Column(String, default='')  # 昵称
    profile_photo = Column(String, default='')  # 头像url
    is_student = Column(Integer, default=0)  # 是否是在校大学生：1YES，0NO
    member_expire_time = Column(TIMESTAMP, default=func.now())  # 会员过期时间
    is_faithful = Column(Integer, default=0)  # 是否诚信：1YES，0NO
    # 认证信息：这些会在一定的产品使用场景中提醒用户去完善，其中认证可以用女性来驱动
    change_detail_message_times = Column(Integer, default=0)  # 修改详细信息的次数
    mobile_address_book_status = Column(Integer, default=0)  # 手机通讯录状态
    identity_auth_status = Column(Integer, default=0)  # 身份证认证状态
    voice_auth_status = Column(Integer, default=0)  # 声音识别状态
    face_auth_status = Column(Integer, default=0)  # 人脸识别状态
    fingerprint_auth_status = Column(Integer, default=0)  # 指纹认证状态
    education_certificate_status = Column(Integer, default=0)  # 教育认证状态
    employment_certificate_status = Column(Integer, default=0)  # 工作认证状态
    user_info_fill_count = Column(Integer, default=0)  # 详细信息完善进度（条目数量）
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class UserInfo(Base):
    """用户数据，就是自身条件信息"""
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer, default=0)  # user_id -- index --
    sex = Column(Integer, default=-1)  # 性别：0FEMALE 1MALE
    married_times = Column(Integer, default=0)  # 结过婚次数
    child_num = Column(Integer, default=0)  # 当前拥有孩子数量
    year_of_birth = Column(Integer, default=1970)  # 出生年份
    annual_income = Column(Integer, default=0)  # 年收入（税前万）
    height = Column(Integer, default=0)  # 身高（cm）
    weight = Column(Integer, default=0)  # 体重（kg）
    degree = Column(Integer, default=0)  # 学历: 见DEGREE_DICT
    seniority = Column(Integer, default=0)  # 工龄
    house_value = Column(Integer, default=0)  # 房产价值
    car_value = Column(Integer, default=0)  # 汽车价值
    home_province = Column(String, default='')  # 家乡省份
    home_city = Column(String, default='')  # 家乡城市
    live_province = Column(String, default='')  # 居住省份
    live_city = Column(String, default='')  # 居住城市
    collage_province = Column(String, default='')  # 最新大学省份
    collage_city = Column(String, default='')  # 最新大学城市
    collage = Column(String, default='')  # 最新大学名称
    profession = Column(String, default='')  # 专业
    vocation = Column(String, default='')  # 职业
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间
