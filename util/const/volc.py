#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""火山引擎调用参数。地址和资源号来自豆包语音、火山方舟公开文档。"""

# 录音文件极速版：一次请求返回文本，不走提交再查询。
# https://docs.volcengine.com/docs/6561/1631584
ASR_FLASH_URL = 'https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash'
ASR_RESOURCE_ID = 'volc.bigasr.auc_turbo'
ASR_MODEL_NAME = 'bigmodel'
ASR_SEQUENCE = '-1'
ASR_AUDIO_FORMAT = 'mp3'
ASR_LANGUAGE = 'zh-CN'
ASR_USER_ID = 'guan'
ASR_TIMEOUT_SECONDS = 30

ASR_STATUS_OK = '20000000'
ASR_STATUS_SILENCE = '20000003'
ASR_STATUS_EMPTY_AUDIO = '45000002'
ASR_EMPTY_STATUSES = frozenset({ASR_STATUS_SILENCE, ASR_STATUS_EMPTY_AUDIO})

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
