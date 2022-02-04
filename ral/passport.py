#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'


def get_login_key(access_token):
    """
    返回登录查询 redis 的 key
    :return:
    """
    return 'access_token:' + access_token


def get_access_token_key(user_id):
    """
    返回 ac 查询的 key
    :param user_id:
    :return:
    """
    return 'user_id:' + str(user_id) + ':access_token'


def put_access_token(redis, user_id, access_token):
    """
    写入 uid 和 ac 的对应关系
    :param redis:
    :param user_id:
    :param access_token:
    :return:
    """
    return redis.set(get_access_token_key(user_id), access_token)


def get_access_token(redis, user_id):
    """
    获取 uid 和 ac 的对应关系
    :param redis:
    :param user_id:
    :return:
    """
    return redis.get(get_access_token_key(user_id))


def put_current_user_info(redis, access_token, current_user_info):
    """
    把当前登录用户的基本信息放到 redis, 如果 redis 已有记录, 就更新, 如果没有, 就新增
    :param redis:
    :param access_token:
    :param current_user_info:
    :return:
    """
    current_user_info_json = current_user_info.__dict__
    current_user_info_json = {
        k: current_user_info_json[k]
        for k in current_user_info_json
        if k in ['id', 'phone']
    }
    redis.hmset(get_login_key(access_token), current_user_info_json)
    return current_user_info_json


def del_current_user_info(redis, access_token):
    """
    删除登录的用户信息
    :param redis:
    :param access_token:
    :return:
    """
    redis.delete(get_login_key(access_token))


def get_current_user_info(redis, access_token):
    """
    从 redis 获取当前登录用户的信息
    :param redis:
    :param access_token:
    :return:
    """
    return redis.hgetall(get_login_key(access_token))
