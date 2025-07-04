#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.31 11:55
# @Author  : yida
# @File    : ass_to_srt.py
# @Software: PyCharm
import os.path
import re

from utils.file_utils import FileUtils
from utils.string_utils import StringUtils

"""
将ass格式字幕转换为srt格式字幕
"""


def ass_to_srt(ass_file_path, srt_file_path=None, encoding: str = 'utf-8'):
    if not os.path.exists(ass_file_path):
        print(f"ass字幕文件{ass_file_path}不存在,无法进行字幕格式转换.")
        return False, None

    ass_content = FileUtils.read_file_as_string(ass_file_path, encoding=encoding)
    if StringUtils.is_empty(ass_content):
        print(f"ass字幕文件{ass_file_path}内容为空,无法进行字幕格式转换.")
        return False, None
    srt_entries = []
    in_events = False
    entry_count = 0

    for line in ass_content.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 检测[Events]区块开始
        if line.lower().startswith('[events]'):
            in_events = True
            continue

        if in_events and line.startswith('Dialogue:'):
            entry_count += 1
            # 分割前9个逗号，第10部分为文本
            parts = line.split(',', 9)
            if len(parts) < 10:
                continue

            # 提取时间轴和文本
            start_time = parts[1].strip()
            end_time = parts[2].strip()
            text = parts[9].strip()

            # 转换时间格式
            srt_start = convert_time(start_time)
            srt_end = convert_time(end_time)

            # 清理文本内容
            cleaned_text = clean_text(text)

            # 构建SRT条目
            srt_entry = {
                "id": int(entry_count),
                "time_range": srt_start + " --> " + srt_end,
                "start_time": srt_start,
                "end_time": srt_end,
                "subtitle": cleaned_text
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


def convert_time(ass_time):
    """
    转换ASS时间格式为SRT格式
    ASS示例: 00:09:47.51 → SRT示例: 00:09:47,510
    """
    if '.' in ass_time:
        time_part, fraction = ass_time.split('.', 1)
        # 将百分秒补全为三位毫秒
        milliseconds = fraction.ljust(3, '0')[:3]
        return f"{time_part},{milliseconds}"
    else:
        return f"{ass_time},000"


def clean_text(text):
    # 移除所有{}包裹的特效标签
    text = re.sub(r'\{.*?\}', '', text)
    # 转换ASS换行符为SRT换行符
    text = text.replace('\\N', '\n')
    # 去除首尾空白
    return text.strip()


if __name__ == '__main__':
    ass_file_path = "E:/BadiduNetDiskDownload/功夫.ass"
    srt_file_path = "E:/BadiduNetDiskDownload/功夫_test.srt"
    fps = 13978
    convert_result, srt_entries = ass_to_srt(ass_file_path, srt_file_path)
    if convert_result:
        subtitle_content_json = StringUtils.to_json_str(srt_entries)
        print(f"字幕格式转换成功,字幕文件保存在{srt_file_path}, 字幕内容为:\n{subtitle_content_json}")
    else:
        print(f"字幕格式转换失败,请检查输入文件{ass_file_path}")
