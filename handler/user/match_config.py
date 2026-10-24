#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from handler.basehandler import BaseHandler
from service.match_config import MatchConfigService
from service.voice_pipeline import VoicePipeline
from util.const.identity import MAX_VOICE_BYTES
from util.const.response import RESP_NEED_LOGIN, RESP_VOICE_MISSING, RESP_VOICE_TOO_LARGE
from util.monitor import superMonitor, Response

logger = logging.getLogger(__name__)


class MatchConfigHandler(BaseHandler):
    """匹配配置接口：GET 查询双侧数据，PUT 更新（语音文字 → 提取条件/期望）"""

    @superMonitor
    def get(self):
        mcs = MatchConfigService(self.currentPassport)
        return Response(data=mcs.getMatchConfig())

    @superMonitor
    def put(self):
        voice_text = self.getRequestParameter('voiceText', default='')
        if not voice_text:
            return Response(msg={'code': 1003, 'errMsg': 'voiceText 不能为空'})
        outcome = MatchConfigService(self.currentPassport).updateFromVoiceText(voice_text)
        if outcome.rejected:
            return Response(msg=outcome.msg)
        return Response(data=outcome.data, msg=outcome.msg)


class VoiceTextHandler(BaseHandler):
    """上传原始语音：加密保存，再把语音和提示词一次交给方舟提取。"""

    @superMonitor
    def post(self):
        if not self.currentPassportId:
            return Response(msg=RESP_NEED_LOGIN)
        audio_bytes = self._audio_bytes()
        if not audio_bytes:
            return Response(msg=RESP_VOICE_MISSING)
        if len(audio_bytes) > MAX_VOICE_BYTES:
            logger.warning("语音超过大小限制 passport=%s bytes=%s", self.currentPassportId, len(audio_bytes))
            return Response(msg=RESP_VOICE_TOO_LARGE)
        outcome = VoicePipeline(self.currentPassport).run(audio_bytes)
        if outcome.rejected:
            return Response(msg=outcome.msg)
        return Response(data=outcome.data, msg=outcome.msg)

    def _audio_bytes(self):
        audio_data = self.request.files.get('audio')
        if not audio_data:
            return b''
        return audio_data[0].get('body') or b''
