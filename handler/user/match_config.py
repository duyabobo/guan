#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import tempfile

from handler.basehandler import BaseHandler
from service.match_config import MatchConfigService
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
        mcs = MatchConfigService(self.currentPassport)
        data = mcs.updateFromVoiceText(voice_text)
        return Response(data=data)


class VoiceTextHandler(BaseHandler):
    """语音识别接口：接收音频文件，返回识别文字"""

    @superMonitor
    def post(self):
        audio_data = self.request.files.get('audio')
        if not audio_data:
            return Response(code=400, msg="缺少音频文件")

        audio_bytes = audio_data[0]['body']
        recognized_text = self._transcribe(audio_bytes)
        return Response(data={"text": recognized_text})

    def _transcribe(self, audio_bytes):
        """调用 Whisper 识别音频，返回文本"""
        try:
            import openai
            from util.config import get_conf
        except ImportError:
            logger.error("openai package not installed")
            return ""

        api_key = get_conf("openai_api_key", "")
        api_base = get_conf("openai_api_base", "https://api.openai.com/v1")

        if not api_key:
            logger.warning("openai_api_key not configured")
            return ""

        client = openai.OpenAI(api_key=api_key, base_url=api_base)

        # 写到临时文件（Whisper API 需要文件对象）
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, 'rb') as f:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="zh",
                )
            text = result.text
            logger.info("voice transcription done, text length=%d", len(text))
            return text
        finally:
            os.unlink(tmp_path)
