#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.28 18:38
# @Author  : yida
# @File    : srt_to_sub.py
# @Software: PyCharm


import re

from utils.object_utils import ObjectUtils
from utils.video_utils import VideoUtils


def parse_srt(srt_file, fps):
    subtitles = []
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    entries = content.strip().split("\n\n")
    for entry in entries:
        lines = entry.splitlines()
        lines = [item for item in lines if item != '']
        if len(lines) >= 3:
            index = int(lines[0])
            time_range = lines[1]
            text = "\n".join(lines[2:])
            start_time, end_time = parse_time_range(time_range, fps)
            subtitles.append((start_time, end_time, text.strip()))
    return subtitles


def time_to_frames(time_str, fps):
    # 处理逗号/冒号分隔的毫秒（兼容不同格式）
    if ',' in time_str:
        hhmmss, ms = time_str.split(',')
    else:
        hhmmss, ms = time_str.split('.') if '.' in time_str else (time_str, '0')

    # 分解小时、分钟、秒
    h, m, s = map(int, hhmmss.split(':'))
    # 计算总秒数（含毫秒）
    total_seconds = h * 3600 + m * 60 + s + int(ms) / 1000
    # 计算帧数（考虑NTSC的精确帧率23.976=24000/1001）
    frames = total_seconds * (fps * 1000 / 1001) if abs(fps - 23.976) < 0.01 else total_seconds * fps
    return round(frames)


def parse_time_range(srt_time, fps):
    start, end = srt_time.split(' --> ')
    start_frame = time_to_frames(start.strip(), fps)
    end_frame = time_to_frames(end.strip(), fps)
    return start_frame, end_frame


def convert_time_format(srt_time):
    hours, minutes, seconds, milliseconds = re.split('[:.,]', srt_time)
    total_milliseconds = (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int(milliseconds)
    return total_milliseconds


def write_sub(subtitles, sub_file):
    write_result = True
    try:
        with open(sub_file, 'w', encoding='utf-8') as f:
            for start, end, text in subtitles:
                f.write(f'{{{start}}}{{{end}}}{text}\n')
    except:
        write_result = False
    finally:
        return write_result


def srt_to_sub(srt_file_path, sub_file_path=None, fps=0, key_mappings: dict = None):
    if fps is None or fps <= 0:
        print("fps参数为必填项,若fps参数未知,则无法精确转换为sub格式.")
        return False, None
    subtitles = parse_srt(srt_file_path, fps)
    if subtitles is None or len(subtitles) <= 0:
        print(f"解析srt字幕文件{srt_file_path}失败.")
        return False, None
    if sub_file_path is None or len(sub_file_path) <= 0:
        if key_mappings is None or len(key_mappings) <= 0:
            convert_result = (subtitles is not None and len(subtitles) > 0)
            return convert_result, subtitles
        subtitles = [ObjectUtils.tuple_2_dict(item, key_mappings) for item in subtitles]
        convert_result = (subtitles is not None and len(subtitles) > 0)
        return convert_result, subtitles
    write_result = write_sub(subtitles, sub_file_path)
    return write_result, subtitles


if __name__ == "__main__":
    video_path = "E:/BadiduNetDiskDownload/功夫.avi"
    srt_file = "E:/BadiduNetDiskDownload/功夫.srt"
    sub_file = "E:/BadiduNetDiskDownload/功夫222.sub"
    fps = VideoUtils.get_fps_of(video_path)
    srt_to_sub(srt_file, sub_file, fps, key_mappings=None)
    print(f'Converted {srt_file} to {sub_file} successfully!')
