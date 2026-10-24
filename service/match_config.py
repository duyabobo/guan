#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""匹配配置：语音提取后，按维度写入 profile_attr。"""
import logging

from model.profile_attr import ProfileAttrModel
from service import BaseService
from service.common.page_copy import match_config_copy
from service.common.profile_board import ProfileBoardService
from service.common.profile_catalog import SCOPE_INFO, SCOPE_REQUIREMENT, values_from_payload
from service.common.profile_guard import ProfileWriteOutcome, decide_profile_write
from service.common.voice_gate import voice_entry_blocked
from util.const.response import RESP_VOICE_IN_PROGRESS

logger = logging.getLogger(__name__)


class MatchConfigService(BaseService):

    def __init__(self, passport):
        self.passport = passport
        self.passportId = passport.get('id', 0)
        super(MatchConfigService, self).__init__()

    def getMatchConfig(self):
        blocked = voice_entry_blocked(self.passportId)
        return {
            "copy": match_config_copy(),
            "rows": ProfileBoardService.rows_for(self.passportId, show_all=True),
            "voiceEnabled": not blocked,
            "voiceBlockText": RESP_VOICE_IN_PROGRESS["errMsg"] if blocked else "",
        }

    def updateFromVoiceText(self, voice_text):
        blocked = self._blocked_outcome()
        if blocked is not None:
            return blocked
        extracted = self._extract_from_text(voice_text)
        if not extracted:
            logger.warning("LLM 提取结果为空，原文长度=%s", len(voice_text or ""))
            return self._unchanged_outcome()
        return self.apply_extracted(extracted)

    def apply_extracted(self, extracted):
        """拒绝时不写库。锁定维度冲突则保留旧值，其余照常写入。"""
        blocked = self._blocked_outcome()
        if blocked is not None:
            return blocked
        if not extracted:
            return self._unchanged_outcome()
        return self._write_extracted(extracted)

    def _write_extracted(self, extracted):
        info_values = values_from_payload(SCOPE_INFO, extracted.get("my_info") or {})
        requirement_values = values_from_payload(SCOPE_REQUIREMENT, extracted.get("my_requirement") or {})
        existing = ProfileAttrModel.listByPassportId(self.passportId)
        outcome = decide_profile_write(existing, info_values, requirement_values)
        if outcome.rejected:
            logger.info("资料写入被拒绝 passport=%s code=%s", self.passportId, outcome.msg.get("code"))
            return outcome
        ProfileBoardService.save_packed(self.passportId, SCOPE_INFO, outcome.info_values)
        ProfileBoardService.save_packed(self.passportId, SCOPE_REQUIREMENT, outcome.requirement_values)
        if outcome.conflict_labels:
            logger.info(
                "资料锁定冲突，保留旧值 passport=%s dims=%s",
                self.passportId, outcome.conflict_labels,
            )
        outcome.data = self.getMatchConfig()
        return outcome

    def _unchanged_outcome(self):
        return ProfileWriteOutcome(data=self.getMatchConfig())

    def _blocked_outcome(self):
        if not voice_entry_blocked(self.passportId):
            return None
        return ProfileWriteOutcome(msg=RESP_VOICE_IN_PROGRESS, rejected=True)

    def _extract_from_text(self, text):
        try:
            from service.llm_extract import LlmExtractService
            return LlmExtractService.extractMatchConfig(text)
        except Exception as e:
            logger.exception("LLM 提取异常: %s", e)
            return None
