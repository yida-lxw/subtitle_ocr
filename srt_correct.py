#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.25 16:29
# @Author  : yida
# @File    : srt_correct.py
# @Software: PyCharm
from config.app_config import APPConfig
from llm_chat import assemble_param, post, answer_content, assemble_param_with_file, post_with_file

"""
借助大模型对提取的字幕文本进行修正
"""

def subtitle_correct(source_subtitle_content, app_config: APPConfig):
    if source_subtitle_content is None or len(source_subtitle_content) <= 0:
        return source_subtitle_content
    try:
        llm_model_name = app_config.llm_model_name
        llm_api_url = app_config.llm_api_url
        llm_api_key = app_config.llm_api_key
        llm_prompt = app_config.llm_prompt
        param_json = assemble_param(source_subtitle_content, llm_model_name, llm_prompt)
        response_json = post(llm_api_url, llm_api_key, param_json)
        answer = answer_content(response_json)
        return answer
    except Exception as e:
        answer = source_subtitle_content
        return answer

