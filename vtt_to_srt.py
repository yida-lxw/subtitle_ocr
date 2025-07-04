#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.31 17:27
# @Author  : yida
# @File    : vtt_to_srt.py
# @Software: PyCharm
import os
import re

from utils.file_utils import FileUtils
from utils.string_utils import StringUtils

"""
vtt格式字幕转换为srt格式
"""


def webvtt_to_srt(vtt_file_path, encoding: str = 'utf-8'):
    if not os.path.exists(vtt_file_path):
        print(f"vtt字幕文件{vtt_file_path}不存在,无法进行字幕格式转换.")
        return False, None

    vtt_content = FileUtils.read_file_as_string(vtt_file_path, encoding=encoding)
    if StringUtils.is_empty(vtt_content):
        print(f"vtt字幕文件{vtt_file_path}内容为空,无法进行字幕格式转换.")
        return False, None

    # 处理特殊字符和BOM头
    cleaned_content = vtt_content.lstrip('\ufeff').replace('\r\n', '\n')

    # 分割字幕块的正则表达式
    block_pattern = re.compile(
        r'((?:\d{1,2}:)?\d{2}:\d{2}[.,]\d{3})\s*-->\s*((?:\d{1,2}:)?\d{2}:\d{2}[.,]\d{3})'
    )

    # 移除WEBVTT头及元数据
    lines = [line for line in cleaned_content.split('\n')
             if not line.strip().startswith(('WEBVTT', 'NOTE', 'STYLE', 'REGION'))]

    srt_blocks = []
    counter = 1
    current_block = {}

    for line in lines:
        line = line.strip()
        if len(line) <= 0:
            continue
        # 检测时间轴行
        if block_pattern.match(line):
            if len(current_block) == 0:
                current_block = process_block(line, counter)
                counter += 1
        elif line:
            # 移除HTML标签和多余空格
            line = re.sub(r'<\/?[^>]+>', '', line).strip()
            current_block["subtitle"] = line
            srt_blocks.append(current_block)
            current_block = {}

    # 处理最后一个未闭合块
    if len(current_block) > 0:
        current_block = process_block(current_block, counter)
        srt_blocks.append(current_block)
        current_block = {}
    convert_result = (srt_blocks is not None and len(srt_blocks) > 0)
    return convert_result, srt_blocks


"""
将SRT字幕转换为WebVTT格式
"""


def srt_to_webvtt(srt_file_path, encoding: str = 'utf-8'):
    if not os.path.exists(srt_file_path):
        print(f"srt字幕文件{srt_file_path}不存在,无法进行字幕格式转换.")
        return False, None

    srt_content = FileUtils.read_file_as_string(srt_file_path, encoding=encoding)
    if StringUtils.is_empty(srt_content):
        print(f"srt字幕文件{srt_file_path}内容为空,无法进行字幕格式转换.")
        return False, None
    subtitle_entries = []
    # 使用正则匹配SRT时间轴格式
    timecode_pattern = re.compile(
        r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
    )

    lines = srt_content.split('\n')
    item_entry = {}
    subtitle_entries.append(
        {
            "webvtt": "WEBVTT",
            "start_time": "",
            "end_time": "",
            "subtitle": ""
        }
    )
    for line in lines:
        line = line.strip()
        # 处理时间轴行
        if timecode_pattern.match(line):
            # 替换逗号为点并添加箭头
            new_line = line.replace(',', '.')
            time_range_group = new_line.split(' --> ')
            start_time = time_range_group[0]
            end_time = time_range_group[1]
            item_entry["start_time"] = start_time
            item_entry["end_time"] = end_time

        # 处理字幕文本行
        elif line and not line.isdigit():
            item_entry["subtitle"] = line
        # 完成一个条目处理
        elif (line is None or len(line) <= 0) and len(item_entry) > 0:
            subtitle_entries.append(item_entry)
            item_entry = {}

    # 处理最后一个未闭合的条目
    if len(item_entry) > 0:
        subtitle_entries.append(item_entry)
        item_entry = {}
    convert_result = len(subtitle_entries) > 0
    return convert_result, subtitle_entries


def process_block(line: str, index: int) -> dict:
    """处理单个字幕块的格式"""
    if "." in line:
        line = line.replace('.', ',', 2)
    timecodeGroup = line.split(' --> ')
    start_time = timecodeGroup[0]
    end_time = timecodeGroup[1]
    return {
        "id": index,
        "start_time": start_time,
        "end_time": end_time
    }


if __name__ == '__main__':
    srt_file_path = "E:/BadiduNetDiskDownload/功夫.srt"
    convert_result, srt_entries = srt_to_webvtt(srt_file_path)
    if convert_result:
        subtitle_content_json = StringUtils.to_json_str(srt_entries)
        print(f"字幕格式转换成功, 字幕内容为:\n{subtitle_content_json}")
    else:
        print(f"字幕格式转换失败,请检查输入文件{srt_file_path}")
