#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""火山方舟调用参数。语音和提示词一次送入方舟，不再单独调用语音识别。"""

# 方舟对话接口，OpenAI SDK 兼容。
# https://ark.volcengine.com/region:cn-beijing/docs/compatible-with-openai-sdk
ARK_API_BASE = 'https://ark.cn-beijing.volces.com/api/v3'
ARK_MODEL = 'doubao-seed-2-1-lite-260915'
ARK_TIMEOUT_SECONDS = 20
ARK_MAX_TOKENS = 512
ARK_AUDIO_TIMEOUT_SECONDS = 45
ARK_AUDIO_MAX_TOKENS = 1024
ARK_AUDIO_FORMAT = 'mp3'
ARK_TEMPERATURE = 0.1
ARK_THINKING_DISABLED = 'disabled'
