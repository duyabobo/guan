#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from service.common.profile_guard import ProfileWriteOutcome
from service.common.voice_gate import voice_entry_blocked
from service.llm_extract import LlmExtractService
from service.match_config import MatchConfigService
from service.sensitive.vault import SensitiveVault
from util.const.identity import KIND_VOICE, VOICE_CONTENT_TYPE
from util.const.response import RESP_IDENTITY_INCOMPLETE, RESP_VOICE_IN_PROGRESS

logger = logging.getLogger(__name__)


class VoicePipeline(object):
    """原始语音先在内存里加密，再连同提示词一次提交给方舟，最后把密文落库。"""

    def __init__(self, passport):
        self.passport = passport
        self.passport_id = int(passport.get('id') or 0)

    def run(self, audio_bytes):
        if voice_entry_blocked(self.passport_id):
            return ProfileWriteOutcome(msg=RESP_VOICE_IN_PROGRESS, rejected=True)
        vault = SensitiveVault()
        sealed = vault.seal(self.passport_id, KIND_VOICE, audio_bytes, VOICE_CONTENT_TYPE)
        if not sealed:
            logger.warning("语音加密失败，需要重新登录 passport=%s", self.passport_id)
            return ProfileWriteOutcome(msg=RESP_IDENTITY_INCOMPLETE, rejected=True)
        vault.release_read()
        extracted = LlmExtractService.extract_from_audio(audio_bytes)
        outcome = self._config_from(extracted)
        if outcome.rejected:
            return outcome
        record_id = vault.keep(sealed)
        if not extracted:
            logger.warning("语音提取结果为空 passport=%s record=%s", self.passport_id, record_id)
        return outcome

    def _config_from(self, extracted):
        service = MatchConfigService(self.passport)
        if not extracted:
            outcome = service.apply_extracted(None)
            if outcome.data is not None:
                outcome.data["text"] = ""
            return outcome
        outcome = service.apply_extracted(extracted)
        if outcome.rejected or outcome.data is None:
            return outcome
        outcome.data["text"] = str(extracted.get("transcript") or "").strip()
        return outcome
