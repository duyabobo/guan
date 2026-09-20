#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM 信息提取服务：从自然语言文本中提取匹配配置的结构化字段。
依赖 openai SDK，需在 requirements.txt 中添加 openai>=1.0.0。
"""
import json
import logging

from util.config import get_conf

logger = logging.getLogger(__name__)

# 提取 Prompt 模板
_EXTRACT_PROMPT = """
你是一个信息提取助手，帮用户从自然语言中提取婚恋匹配配置。

用户输入文本（来自语音识别）：
{text}

请从文本中提取以下两类信息，以 JSON 格式返回：
1. "my_info"（我的条件）：性别(sex)、出生年份(birth_year)、身高cm(height)、体重kg(weight)、学历级别(education_level)、入学年份(study_from_year)
2. "my_requirement"（我的期望）：对方性别(sex)、年龄范围(min_birth_year/max_birth_year)、身高范围(min_height/max_height)

只提取文本中明确提到的字段，未提及的不要猜测。
返回格式示例：
{{
  "my_info": {{"sex": 1, "birth_year": 1995, "height": 170}},
  "my_requirement": {{"min_height": 165, "max_height": 185}}
}}

注意：sex 字段值：1=男，2=女。学历级别（education_level）：1=高中及以下, 2=大专, 3=本科, 4=硕士, 5=博士。
只返回 JSON，不要有其他说明。
"""


class LlmExtractService:

    @staticmethod
    def extractMatchConfig(text):
        """
        从自然语言文本中提取婚恋配置字段。
        返回 dict: {"my_info": {...}, "my_requirement": {...}}
        """
        try:
            import openai
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai>=1.0.0")
            return None

        api_key = get_conf("openai_api_key", "")
        api_base = get_conf("openai_api_base", "https://api.openai.com/v1")
        model = get_conf("openai_model", "gpt-4o-mini")

        if not api_key:
            logger.warning("openai_api_key not configured, skip LLM extraction")
            return None

        client = openai.OpenAI(api_key=api_key, base_url=api_base)
        prompt = _EXTRACT_PROMPT.format(text=text)

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=512,
        )
        content = response.choices[0].message.content.strip()
        logger.info("LLM extraction result: %s", content[:200])

        return json.loads(content)
