#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'


def getLoginKey(accessToken):
    """
    返回登录查询 redis 的 key
    :return:
    """
    return 'accessToken:' + accessToken


def getAccessTokenKey(uid):
    """
    返回 ac 查询的 key
    :param uid:
    :return:
    """
    return 'uid:' + str(uid) + ':accessToken'


def putAccessToken(redis, uid, accessToken):
    """
    写入 uid 和 ac 的对应关系
    :param redis:
    :param uid:
    :param accessToken:
    :return:
    """
    return redis.set(getAccessTokenKey(uid), accessToken)


def getAccessToken(redis, uid):
    """
    获取 uid 和 ac 的对应关系
    :param redis:
    :param uid:
    :return:
    """
    return redis.get(getAccessTokenKey(uid))


def putCurrentUserInfo(redis, accessToken, currentUserInfo):
    """
    把当前登录用户的基本信息放到 redis, 如果 redis 已有记录, 就更新, 如果没有, 就新增
    :param redis:
    :param accessToken:
    :param currentUserInfo:
    :return:
    """
    currentUserInfoJson = currentUserInfo.__dict__
    currentUserInfoJson = {
        k: currentUserInfoJson[k]
        for k in currentUserInfoJson
        if k in ['id', 'phone']
    }
    redis.hmset(getLoginKey(accessToken), currentUserInfoJson)
    return currentUserInfoJson


def delCurrentUserInfo(redis, accessToken):
    """
    删除登录的用户信息
    :param redis:
    :param accessToken:
    :return:
    """
    redis.delete(getLoginKey(accessToken))


def getCurrentUserInfo(redis, accessToken):
    """
    从 redis 获取当前登录用户的信息
    :param redis:
    :param accessToken:
    :return:
    """
    return redis.hgetall(getLoginKey(accessToken))
