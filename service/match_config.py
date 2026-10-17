#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""匹配配置：语音文字提取后，按维度写入 profile_attr。"""
import logging

from service import BaseService
from service.common.page_copy import match_config_copy
from service.common.profile_board import ProfileBoardService
from service.common.profile_catalog import SCOPE_INFO, SCOPE_REQUIREMENT

logger = logging.getLogger(__name__)


class MatchConfigService(BaseService):

    def __init__(self, passport):
        self.passport = passport
        self.passportId = passport.get('id', 0)
        super(MatchConfigService, self).__init__()

    def getMatchConfig(self):
        return self._config_of()

    def updateFromVoiceText(self, voiceText: str) -> dict:
        extracted = self._extractFromText(voiceText)
        if not extracted:
            logger.warning("LLM 提取结果为空，原文: %s", voiceText[:100])
            return self.getMatchConfig()

        self._save_scope(SCOPE_INFO, extracted.get("my_info") or {})
        self._save_scope(SCOPE_REQUIREMENT, extracted.get("my_requirement") or {})
        return self.getMatchConfig()

    def _config_of(self):
        return {
            "copy": match_config_copy(),
            "rows": ProfileBoardService.rows_for(self.passportId),
        }

    def _extractFromText(self, text: str) -> dict | None:
        try:
            from service.llm_extract import LlmExtractService
            return LlmExtractService.extractMatchConfig(text)
        except Exception as e:
            logger.exception("LLM 提取异常: %s", e)
            return None

    def _save_scope(self, scope, payload):
        if not payload:
            return
        ProfileBoardService.save_extracted(self.passportId, scope, payload)
        logger.info("profile_attr scope=%s passport=%s", scope, self.passportId)
