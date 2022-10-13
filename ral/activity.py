#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 这里维护活动匹配列表逻辑

def getKey(columnName, columnValue):
    return "%s:%s:activityIdSet" % (columnName, str(columnValue))


def addActivityId(key, activityId):
    pass


def remActivityId(key, activityId):
    pass


# 新增活动，全覆盖key填充
def addActivity(activity):
    pass


# 发起邀请，修剪
def inviteActivity(activity, requirement):
    # for ... in columns:
    #   old(全) -> new(邀请者)
    #   remActivityId
    pass


# 取消邀请，等价于addActivity
def uninviteActivity(activity):
    addActivity(activity)
    pass


# 接受邀请，修剪
def acceptActivity(activity, requirement):
    # for ... in columns:
    #   old(邀请者) -> new(null)
    #   remActivityId
    pass


# 取消接受，等价于addActivity+inviteActivity
def unacceptActivity(activity, requirement):
    addActivity(activity)
    inviteActivity(activity, requirement)
    pass


# 发起邀请后修改期望，等价于acceptActivity+addActivity+inviteActivity
def changeRequirement(activity, oldRequirement, newRequirement):
    acceptActivity(activity, oldRequirement)
    addActivity(activity)
    inviteActivity(activity, newRequirement)
