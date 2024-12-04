#! /usr/bin/env python
# -*- coding: utf-8 -*-
from service.qiniu_cdn import MyStorage
from util.const.base import MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNKNOWN
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX, MODEL_STATUS_YES
from util.const.qiniu_img import CDN_QINIU_BOY_HEAD_IMG, CDN_QINIU_GIRL_HEAD_IMG


class GuanHelper(object):

    @classmethod
    def getMatchMeetResult(cls, activity, userInfo):
        if not userInfo:
            return MODEL_MEET_RESULT_UNKNOWN
        return activity.girl_meet_result if userInfo.sex == MODEL_SEX_MALE_INDEX else activity.boy_meet_result


    @classmethod
    def getActivityImg(cls, activity, address, matchUser, currentUser, thumbnailsFlag):
        """
        thumbnailsFlag: 是否缩略图
        """
        # imgUser = None
        # if currentUser and currentUser.passport_id in [activity.girl_passport_id, activity.boy_passport_id]:  # 自己参与就展示自己头像
        #     imgUser = currentUser
        # if matchUser:  # 有异性参与，优先展示异性头像
        #     imgUser = matchUser
        #
        # if imgUser and imgUser.sex in [MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX]:  # 人物头像
        #     if imgUser.has_head_img != MODEL_STATUS_YES:  # 默认头像
        #         return CDN_QINIU_BOY_HEAD_IMG if imgUser.sex == MODEL_SEX_MALE_INDEX else CDN_QINIU_GIRL_HEAD_IMG
        #     elif cls.getMatchMeetResult(activity, imgUser) != MODEL_MEET_RESULT_FIT_CHOICE:  # 虚拟头像
        #         return cls.getUserImg(imgUser, virtualFlag=True, thumbnailsFlag=thumbnailsFlag)
        #     else:  # 真实头像
        #         return cls.getUserImg(imgUser, virtualFlag=False, thumbnailsFlag=thumbnailsFlag)
        # else:  # 地址头像
        #
        if thumbnailsFlag:
            return address.thumbnails_img
        else:
            return address.img

    @classmethod
    def getUserImg(cls, userRecord, virtualFlag, thumbnailsFlag):
        if thumbnailsFlag:
            if virtualFlag:
                return MyStorage.getVirtualThumbnailsImgUrl(userRecord.passport_id, userRecord.head_img_version)
            else:
                return MyStorage.getRealThumbnailsImgUrl(userRecord.passport_id, userRecord.head_img_version)
        else:
            if virtualFlag:
                return MyStorage.getVirtualImgUrl(userRecord.passport_id, userRecord.head_img_version)
            else:
                return MyStorage.getRealImgUrl(userRecord.passport_id, userRecord.head_img_version)
