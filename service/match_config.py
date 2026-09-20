#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
匹配配置服务：语音文字 → 提取我的条件 / 我的期望，并更新用户信息
"""
import json
import logging

from model.requirement import RequirementModel
from model.user import UserModel
from service import BaseService
from service.common.myself_helper import UserHelper
from service.common.requirement_helper import RequirementHelper
from service.myself import UserInfoService
from service.requirement import RequirementService
from util.class_helper import lazy_property
from util.const.match import OP_TYPE_SEX, MODEL_SEX_UNKNOWN_INDEX

logger = logging.getLogger(__name__)


class MatchConfigService(BaseService):
    """匹配配置：聚合展示 + 语音自然语言更新我的条件/我的期望"""

    def __init__(self, passport):
        self.passport = passport
        self.passportId = passport.get('id', 0)
        super(MatchConfigService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    @lazy_property
    def requirementInfo(self):
        return RequirementModel.getByPassportId(self.passportId)

    def _buildMyInfoPairs(self):
        """我的条件（用户信息）简洁版，用于双侧展示"""
        uh = UserHelper(self.userInfo)
        infoList = uh.getInformationList(checkDynamicData=False)
        return [{"desc": i.desc, "value": i.fullValue} for i in infoList if i.fullValue]

    def _buildMyRequirementPairs(self):
        """我的期望（择偶条件）简洁版，用于双侧展示"""
        rh = RequirementHelper(self.requirementInfo)
        reqList = rh.getRequirementList(checkDynamicData=False)
        return [{"desc": r.desc, "value": r.fullValue} for r in reqList if r.fullValue]

    def getMatchConfig(self):
        """返回双侧展示数据"""
        return {
            "myInfoPairs": self._buildMyInfoPairs(),
            "myRequirementPairs": self._buildMyRequirementPairs(),
        }

    def updateFromVoiceText(self, voiceText):
        """
        从语音识别文本中提取并更新我的条件 + 我的期望。
        使用 OpenAI GPT 做结构化信息提取。
        返回更新后的配置数据。
        """
        extracted = self._extractInfoFromText(voiceText)
        if not extracted:
            logger.warning("voice text extraction returned empty: text=%s", voiceText[:100])
            return self.getMatchConfig()

        my_info_updates = extracted.get("my_info", {})
        my_requirement_updates = extracted.get("my_requirement", {})

        if my_info_updates:
            self._applyMyInfoUpdates(my_info_updates)
        if my_requirement_updates:
            self._applyMyRequirementUpdates(my_requirement_updates)

        # 重新构建返回数据（避免缓存影响）
        self.userInfo  # noqa: 触发 lazy_property 重新加载在调用方需 invalidate
        return self.getMatchConfig()

    def _extractInfoFromText(self, text):
        """调用 LLM 从自然语言提取结构化字段，返回 dict or None"""
        try:
            from service.llm_extract import LlmExtractService
            return LlmExtractService.extractMatchConfig(text)
        except ImportError:
            logger.warning("LlmExtractService not available, skip extraction")
            return None
        except Exception as e:
            logger.exception("LLM extraction failed: %s", e)
            return None

    def _applyMyInfoUpdates(self, updates):
        """将提取到的我的条件字段批量应用到用户信息"""
        uis = UserInfoService(self.passport)
        for op_type, value in updates.items():
            check = uis.checkBeforeUpdate(op_type, value)
            if check:
                logger.info("skip update my_info field=%s reason=%s", op_type, check)
                continue
            uis.updateMyselfInfo(op_type, value)

    def _applyMyRequirementUpdates(self, updates):
        """将提取到的我的期望字段批量应用到期望配置"""
        rs = RequirementService(self.passportId)
        for op_type, value in updates.items():
            check = rs.checkBeforeUpdate(op_type, value)
            if check:
                logger.info("skip update my_requirement field=%s reason=%s", op_type, check)
                continue
            rs.updateRequirementInfo(op_type, value)
