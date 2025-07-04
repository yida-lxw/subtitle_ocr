#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.25 16:16
# @Author  : yida
# @File    : text_translator.py
# @Software: PyCharm
import os.path

from zhconv import convert

from utils.file_utils import FileUtils
from utils.string_utils import StringUtils

"""
将指定繁体文本内容转换为简体文本内容
"""


def traditional_to_simple_with_text(source_text):
    if StringUtils.is_empty(source_text):
        print("输入的文本为空,无法执行繁简转换处理.")
        return source_text
    simplified_text = convert(source_text, 'zh-hans')
    return simplified_text


"""
将指定文件中的繁体文本内容转换为简体文本内容
"""


def traditional_to_simple_with_file(srt_file_path):
    if not os.path.exists(srt_file_path):
        print(f"文件{srt_file_path}不存在,无法执行文件内容繁简转换处理.")
        return None
    source_text = FileUtils.read_file_as_string(srt_file_path, encoding="utf8")
    simplified_text = traditional_to_simple_with_text(source_text)
    return simplified_text


if __name__ == '__main__':
    srt_file_path = "D:/tmp/srts/segment_00001_00005.srt"
    translated_text = traditional_to_simple_with_file(srt_file_path)
    print(f"转换后的简体内容为:{translated_text}")
