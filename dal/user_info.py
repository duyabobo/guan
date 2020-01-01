#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from datetime import datetime

from models import UserInfo


def add_user_info(db_session, user_id):
    """
    添加一个男性用户信息记录
    :param db_session:
    :param user_id:
    :return:
    """
    user_info = UserInfo(user_id=user_id)
    db_session.add(user_info)
    db_session.flush()
    return user_info


def get_user_info_by_uid(db_session, user_id):
    """
    根据id查询用户信息
    :param db_session:
    :param user_id:
    :return:
    """
    return db_session.query(UserInfo).filter(UserInfo.user_id == user_id).first()


def update_user_info(
        db_session,
        user_info,
        sex,
        married_times,
        child_num,
        age,
        annual_income,
        height,
        weight,
        degree,
        seniority,
        house_value,
        car_value,
        home_province,
        home_city,
        live_province,
        live_city,
        collage_province,
        collage_city,
        collage,
        profession,
        vocation
):
    """
    更新男性用户信息
    :param db_session:
    :param user_info:
    :param sex:
    :param married_times:
    :param child_num:
    :param age:
    :param annual_income:
    :param height:
    :param weight:
    :param degree:
    :param seniority:
    :param house_value:
    :param car_value:
    :param home_province:
    :param home_city:
    :param live_province:
    :param live_city:
    :param collage_province:
    :param collage_city:
    :param collage:
    :param profession:
    :param vocation:
    :return:
    """
    if sex is not None:
        user_info.sex = int(sex)
    if married_times is not None:
        user_info.married_times = married_times
    if child_num is not None:
        user_info.child_num = child_num
    if age is not None:
        user_info.year_of_birth = datetime.now().year - age
    if annual_income is not None:
        user_info.annual_income = annual_income
    if height is not None:
        user_info.height = height
    if weight is not None:
        user_info.weight = weight
    if degree is not None:
        user_info.degree = degree
    if seniority is not None:
        user_info.seniority = seniority
    if house_value is not None:
        user_info.house_value = house_value
    if car_value is not None:
        user_info.car_value = car_value
    if home_province is not None:
        user_info.home_province = home_province
    if home_city is not None:
        user_info.home_city = home_city
    if live_province is not None:
        user_info.live_province = live_province
    if live_city is not None:
        user_info.live_city = live_city
    if collage_province is not None:
        user_info.collage_province = collage_province
    if collage_city is not None:
        user_info.collage_city = collage_city
    if collage is not None:
        user_info.collage = collage
    if profession is not None:
        user_info.profession = profession
    if vocation is not None:
        user_info.vocation = vocation
    db_session.flush()
