#! /usr/bin/env python
# -*- coding: utf-8 -*-
import io
import logging

from util.config import get_conf
from util.const.identity import VOICE_FILENAME, WHISPER_LANGUAGE, WHISPER_MODEL

logger = logging.getLogger(__name__)


class AsrService(object):

    def transcribe(self, audio_bytes):
        if not audio_bytes:
            return ''
        api_key = get_conf('openai_api_key', '')
        if not api_key:
            logger.warning("openai_api_key 未配置，跳过语音识别")
            return ''
        try:
            import openai
        except ImportError:
            logger.error("未安装 openai，跳过语音识别")
            return ''
        client = openai.OpenAI(api_key=api_key, base_url=get_conf('openai_api_base', 'https://api.openai.com/v1'))
        audio = io.BytesIO(audio_bytes)
        audio.name = VOICE_FILENAME
        try:
            result = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio,
                language=WHISPER_LANGUAGE,
            )
        except Exception as exc:
            logger.exception("语音识别失败 %s", exc)
            return ''
        text = (result.text or '').strip()
        logger.info("语音识别完成 text_length=%s", len(text))
        return text
