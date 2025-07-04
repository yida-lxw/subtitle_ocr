#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.25 17:50
# @Author  : yida
# @File    : llm_chat.py
# @Software: PyCharm
import io
import os

import requests
from utils.string_utils import StringUtils


project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

"""
组装请求llm的请求参数
"""

def assemble_param_with_file(source_subtitle_content, llm_model_name, llm_prompt_file_path):
    with open(project_basepath + llm_prompt_file_path, 'r', encoding='utf-8') as f:
        llm_prompt = f.read()
    param_dict = {
        "stream": False,
        "detail": False,
        "model": llm_model_name,
        "messages": [
            {
                "role": "user",
                "content": llm_prompt
            }
        ],
        "include_thoughts": False
    }
    binary_stream = io.BytesIO(source_subtitle_content.encode('utf-8'))
    files = {
        'file': ("subtitles.txt", binary_stream, 'text/plain')
    }
    return param_dict, files


def assemble_param(source_subtitle_content, llm_model_name, llm_prompt_file_path):
    with open(project_basepath + llm_prompt_file_path, 'r', encoding='utf-8') as f:
        llm_prompt = f.read()

    if "${subtitle_data}" in llm_prompt:
        llm_prompt = llm_prompt.replace("${subtitle_data}", source_subtitle_content)
    param_dict = {
        "stream": False,
        "detail": False,
        "model": llm_model_name,
        "temperature": 0.01,
        "top_p": 0.1,
        "max_tokens": 80960,
        "options": {
            "include_thoughts": False,
            "temperature": 0.7,
            "repeat_penalty": 1.1,
            "chain_of_thought": False
        },
        "messages": [
            {
                "role": "user",
                "content": llm_prompt
            }
        ],
    }
    return param_dict


"""
发送POST请求
"""


def post(llm_api_url: str, llm_api_key: str, param_json: dict) -> dict:
    headers = {
        "Authorization": "Bearer " + llm_api_key,
        "Content-Type": "application/json",
    }

    response = requests.post(llm_api_url, headers=headers, json=param_json)
    return response.json()


def post_with_file(llm_api_url: str, llm_api_key: str, param_json: dict, files) -> dict:
    headers = {
        "Authorization": "Bearer " + llm_api_key,
        "Content-Type": "application/json",
    }

    response = requests.post(llm_api_url, headers=headers, files=files, json=param_json)
    return response.json()

def answer_content(response_json):
    if response_json.get("choices") is not None:
        content = response_json.get("choices")[0].get("message").get("content")
        if StringUtils.is_empty(content):
            return None
        print(f"大模型返回的原始数据:\n{content}")
        final_content = content
        if "<合并后数据>" in final_content:
            while "<合并后数据>" in final_content:
                think_label_index = final_content.find("<合并后数据>")
                final_content = final_content[think_label_index + 7: len(final_content)]
                final_content = final_content.strip()
        if "</合并后数据>" in final_content:
            think_label_index = final_content.find("</合并后数据>")
            final_content = final_content[0 : think_label_index]
            final_content = final_content.strip()

        final_content = final_content.strip()
        if "[]" == final_content or "[\n]" == final_content:
            return None
        if final_content.endswith("</"):
            final_content = final_content[0: len(final_content) - 2]
            final_content = final_content.strip()
        return final_content
    return None


# if __name__ == '__main__':
#     llm_model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
#     llm_api_url = "http://192.168.0.55:3000/v1/chat/completions"
#     llm_api_key = "sk-fCnEQ180qhfbPIH1215150F3Fd864cCdA95aF796B0C6CaE4"
#     param_file_path = "E:/python_projects/subtitle-extraction/param.txt"
#     source_subtitle_content = FileUtils.read_file_as_string(param_file_path)
#     param_json = assemble_param(source_subtitle_content, llm_model_name, propmt_keywords)
#     response_json = post(llm_api_url, llm_api_key, param_json)
#     answer = answer_content(response_json)
#     print(answer)
