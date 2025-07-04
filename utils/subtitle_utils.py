#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.31 15:37
# @Author  : yida
# @File    : subtitle_utils.py
# @Software: PyCharm

import re

from utils.object_utils import ObjectUtils


class SubtitleUtils:
    """
    将srt字幕文本解析为list[dict]
    """

    @staticmethod
    def parse_srt_subtitle(text):
        entries = []
        if ObjectUtils.is_str(text):
            if text is None or len(text) <= 0:
                return text
            lines = text.split('\n')
            if len(lines) <= 0:
                return entries
            lines_groups = ObjectUtils.group_by_four(lines)
            for group_line in lines_groups:
                if len(group_line) < 3:
                    continue
                time_range = group_line[1]
                time_range_group = time_range.split(' --> ')
                start_time = time_range_group[0]
                end_time = time_range_group[1]
                entry = {
                    "id": int(group_line[0]),
                    "time_range": group_line[1],
                    "start_time": start_time,
                    "end_time": end_time,
                    "subtitle": group_line[2]
                }
                entries.append(entry)
        if ObjectUtils.is_list(text):
            for cur_text in text:
                blocks = re.split(r'\n{2,}', cur_text.strip())
                for block in blocks:
                    if block is None or len(block) <= 0:
                        continue
                    lines = block.split('\n')
                    if len(lines) >= 3:
                        time_range = lines[1]
                        time_range_group = time_range.split(' --> ')
                        start_time = time_range_group[0]
                        end_time = time_range_group[1]
                        entry = {
                            "id": int(lines[0]),
                            "time_range": lines[1],
                            "start_time": start_time,
                            "end_time": end_time,
                            "subtitle": lines[2]
                        }
                        entries.append(entry)
        parse_result = (entries is not None and len(entries) > 0)
        return parse_result, entries
