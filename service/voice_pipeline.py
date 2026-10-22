#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from service.asr import AsrService
from service.match_config import MatchConfigService
from service.sensitive.vault import SensitiveVault
from util.const.identity import KIND_VOICE, VOICE_CONTENT_TYPE

logger = logging.getLogger(__name__)


class VoicePipeline(object):
    """原始语音先在内存里加密，识别并抽取后再把密文落库。"""

    def __init__(self, passport):
        self.passport = passport
        self.passport_id = int(passport.get('id') or 0)

    def run(self, audio_bytes):
        vault = SensitiveVault()
        sealed = vault.seal(self.passport_id, KIND_VOICE, audio_bytes, VOICE_CONTENT_TYPE)
        if not sealed:
            return None
        vault.release_read()
        text = AsrService().transcribe(audio_bytes)
        record_id = vault.keep(sealed)
        config = self._config_from(text, record_id)
        config['text'] = text
        return config

    def _config_from(self, text, record_id):
        service = MatchConfigService(self.passport)
        if not text:
            logger.warning("语音识别结果为空 passport=%s record=%s", self.passport_id, record_id)
            return service.getMatchConfig()
        return service.updateFromVoiceText(text)
