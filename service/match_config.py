#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
匹配配置服务：语音文字 → 提取我的条件 / 我的期望，并更新用户信息

LLM 提取字段说明：
  my_info 可提取: sex, birth_year, height, weight, education_level, study_from_year, martial_status
  my_requirement 可提取: sex, min_birth_year, max_birth_year, min_height, max_height,
                          min_weight, max_weight, min_month_pay, max_month_pay, martial_status
"""
import logging

from model.requirement import RequirementModel
from model.user import UserModel
from service import BaseService
from service.common.myself_helper import UserHelper
from service.common.requirement_helper import RequirementHelper
from util.class_helper import lazy_property

logger = logging.getLogger(__name__)


def _pair_from_selector(item):
    """展示行。subDesc 是单位（cm/kg），和见面详情用同一套字段。"""
    return {
        "desc": item.desc,
        "value": item.fullValue,
        "subDesc": getattr(item, "subDesc", "") or "",
    }

# LLM 可提取并直接写库的用户字段白名单（绕过 opType 流程，直接数值落库）
_USER_ALLOWED_FIELDS = frozenset({
    'sex', 'birth_year', 'height', 'weight',
    'martial_status', 'education_level', 'study_from_year',
})

# LLM 可提取并直接写库的期望字段白名单
_REQUIREMENT_ALLOWED_FIELDS = frozenset({
    'sex', 'min_birth_year', 'max_birth_year',
    'min_height', 'max_height',
    'min_weight', 'max_weight',
    'min_month_pay', 'max_month_pay',
    'martial_status', 'education_level',
})


class MatchConfigService(BaseService):
    """匹配配置：聚合展示 + 自然语言更新我的条件/我的期望"""

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

    def getMatchConfig(self):
        """返回双侧展示数据（我的条件 + 我的期望）"""
        return {
            "myInfoPairs":        self._buildMyInfoPairs(),
            "myRequirementPairs": self._buildMyRequirementPairs(),
        }

    def updateFromVoiceText(self, voiceText: str) -> dict:
        """
        从自然语言文本提取结构化字段，更新用户信息 + 期望信息。
        同时保存原始文本，供回溯和二次提取。
        """
        extracted = self._extractFromText(voiceText)
        if not extracted:
            logger.warning("LLM 提取结果为空，原文: %s", voiceText[:100])
            return self.getMatchConfig()

        my_info        = extracted.get("my_info", {})
        my_requirement = extracted.get("my_requirement", {})

        if my_info or voiceText:
            self._saveMyInfo(my_info, raw_text=voiceText)

        if my_requirement or voiceText:
            self._saveMyRequirement(my_requirement, raw_text=voiceText)

        return self._reloadAndGetConfig()

    # ── 内部：展示构建 ────────────────────────────────────────────────────────

    def _buildMyInfoPairs(self):
        uh = UserHelper(self.userInfo)
        info_list = uh.getInformationList(checkDynamicData=False)
        return [_pair_from_selector(i) for i in info_list if i.fullValue]

    def _buildMyRequirementPairs(self):
        rh = RequirementHelper(self.requirementInfo)
        req_list = rh.getRequirementList(checkDynamicData=False)
        return [_pair_from_selector(r) for r in req_list if r.fullValue]

    # ── 内部：LLM 提取 ────────────────────────────────────────────────────────

    def _extractFromText(self, text: str) -> dict | None:
        try:
            from service.llm_extract import LlmExtractService
            return LlmExtractService.extractMatchConfig(text)
        except Exception as e:
            logger.exception("LLM 提取异常: %s", e)
            return None

    # ── 内部：写库 ────────────────────────────────────────────────────────────

    def _saveMyInfo(self, updates: dict, raw_text: str):
        """
        将 LLM 提取的 my_info 字段直接写入 user 表。
        LLM 返回字段名 == model 字段名，白名单过滤后直接落库，不走 opType 流程。
        同时保存原始文本 profile_desc。
        """
        valid = {k: v for k, v in updates.items() if k in _USER_ALLOWED_FIELDS}
        if raw_text:
            valid['profile_desc'] = raw_text
        if valid:
            UserModel.updateByPassportId(passportId=self.passportId, **valid)
            logger.info("my_info 更新字段: %s", list(valid.keys()))

    def _saveMyRequirement(self, updates: dict, raw_text: str):
        """
        将 LLM 提取的 my_requirement 字段直接写入 requirement 表。
        同时保存原始文本 requirement_desc。
        """
        valid = {k: v for k, v in updates.items() if k in _REQUIREMENT_ALLOWED_FIELDS}
        if raw_text:
            valid['requirement_desc'] = raw_text
        if valid:
            RequirementModel.updateByPassportId(self.passportId, **valid)
            # 匹配计数失效
            UserModel.getMatchCnt(passportId=self.passportId, forceRefreshCache=True)
            logger.info("my_requirement 更新字段: %s", list(valid.keys()))

    def _reloadAndGetConfig(self) -> dict:
        """缓存失效后重新构建配置"""
        fresh_user = UserModel.getByPassportId(passportId=self.passportId)
        fresh_req  = RequirementModel.getByPassportId(self.passportId)
        uh = UserHelper(fresh_user)
        rh = RequirementHelper(fresh_req)
        return {
            "myInfoPairs":        [_pair_from_selector(i) for i in uh.getInformationList(False) if i.fullValue],
            "myRequirementPairs": [_pair_from_selector(r) for r in rh.getRequirementList(False) if r.fullValue],
        }
