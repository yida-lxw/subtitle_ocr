#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.31 15:20
# @Author  : yida
# @File    : sub_to_srt.py
# @Software: PyCharm

import os
import re

from utils.file_utils import FileUtils
from utils.string_utils import StringUtils

"""
将sub格式字幕转换为srt格式字幕
"""


def sub_to_srt(sub_file_path, srt_file_path=None, fps: int = 0, encoding: str = 'utf-8'):
    if not os.path.exists(sub_file_path):
        print(f"sub字幕文件{sub_file_path}不存在,无法进行字幕格式转换.")
        return False, None

    sub_content = FileUtils.read_file_as_string(sub_file_path, encoding=encoding)
    if StringUtils.is_empty(sub_content):
        print(f"sub字幕文件{sub_file_path}内容为空,无法进行字幕格式转换.")
        return False, None
    srt_entries = []
    entries = [line.strip() for line in sub_content.split('\n') if line.strip()]

    for idx, entry in enumerate(entries, 1):
        # 使用正则提取帧数和文本（兼容无文本的空字幕情况）
        match = re.match(r'\{(\d+)\}\{(\d+)\}(.*)', entry)
        if not match:
            # 跳过格式错误的行
            continue

        start_frame = int(match.group(1))
        end_frame = int(match.group(2))
        text = match.group(3).strip()

        # 帧数转时间（核心计算）
        start_time = frames_to_time(start_frame, fps)
        end_time = frames_to_time(end_frame, fps)

        # 构建SRT条目
        srt_entry = {
            "id": int(idx),
            "time_range": start_time + " --> " + end_time,
            "start_time": start_time,
            "end_time": end_time,
            "subtitle": text
        }
        srt_entries.append(srt_entry)

    if StringUtils.is_empty(srt_file_path):
        convert_result = (srt_entries is not None and len(srt_entries) > 0)
        return convert_result, srt_entries
    if srt_entries is None or len(srt_entries) <= 0:
        return False, None
    srt_file_path = StringUtils.replaceBackSlash(srt_file_path)
    srt_file_parent_path = os.path.dirname(srt_file_path)
    if not os.path.exists(srt_file_parent_path):
        os.makedirs(srt_file_parent_path)
    entry_size = len(srt_entries)
    counter = 0
    srt_content = ""
    for srt_entry in srt_entries:
        if counter == entry_size - 1:
            srt_entry_str = f"{srt_entry['id']}\n{srt_entry['time_range']}\n{srt_entry['subtitle']}\n"
        else:
            srt_entry_str = f"{srt_entry['id']}\n{srt_entry['time_range']}\n{srt_entry['subtitle']}\n\n\n"
        srt_content = srt_content + srt_entry_str
        counter += 1
    write_result = FileUtils.write_string_to_file(srt_content, srt_file_path)
    return write_result, srt_entries


def frames_to_time(frames, fps: int = 0):
    total_seconds = frames / fps
    hours, remainder = divmod(total_seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds * 1000):03d}"
