#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.28 16:51
# @Author  : yida
# @File    : extract_soft_subtitle.py
# @Software: PyCharm

import json
import os
import subprocess

from utils.file_utils import FileUtils
from utils.os_utils import OSUtils
from utils.string_utils import StringUtils

video_file_suffix_list = [
    "avi",
    "mp4",
    "mkv",
    "mov"
]

def extract_soft_subtitles(source_video_path, ffmpeg_basepath, subtitle_output_dir=None):
    if StringUtils.is_empty(source_video_path):
        print("你尚未输入视频文件，将无法提取视频的内嵌软字幕！")
        return False

    if StringUtils.is_empty(ffmpeg_basepath):
        print("你尚未设置FFmpeg路径，将无法提取视频的内嵌软字幕！")
        return False

    source_video_path = StringUtils.replaceBackSlash(source_video_path)
    source_video_filename = FileUtils.get_filename_with_suffix(source_video_path)
    video_file_suffix = FileUtils.get_suffix(source_video_filename, include_dot=False).lower()
    if video_file_suffix not in video_file_suffix_list:
        print("软字幕提取目前只支持[mkv,mp4,mov]这3种视频格式.")
        return False
    if StringUtils.is_empty(subtitle_output_dir):
        source_video_parent_path = os.path.dirname(source_video_path)
        subtitle_output_dir = source_video_parent_path
    ffmpeg_basepath = StringUtils.replaceBackSlash(ffmpeg_basepath)
    ffmpeg_basepath = StringUtils.to_ends_with_back_slash(ffmpeg_basepath)
    if OSUtils.is_windows():
        ffmpeg_exe_path = ffmpeg_basepath + "bin/ffmpeg.exe"
        ffprobe_exe_path = ffmpeg_basepath + "bin/ffprobe.exe"
    else:
        ffmpeg_exe_path = ffmpeg_basepath + "bin/ffmpeg"
        ffprobe_exe_path = ffmpeg_basepath + "bin/ffprobe"

    if not os.path.exists(ffmpeg_exe_path) or not os.path.exists(ffprobe_exe_path):
        print(f"FFmpeg和FFprobe路径不正确，请检查ffmpeg.exe和ffprobe.exe是否在{ffmpeg_basepath}/bin目录下.")
        return False

    source_video_filename = FileUtils.get_filename_without_suffix(source_video_path)
    source_video_filename_with_suffix = FileUtils.get_filename_with_suffix(source_video_path)
    video_file_suffix = FileUtils.get_suffix(source_video_filename_with_suffix, include_dot=False).lower()

    subtitle_output_dir = StringUtils.replaceBackSlash(subtitle_output_dir)
    subtitle_output_dir = StringUtils.to_ends_with_back_slash(subtitle_output_dir)

    # 创建输出目录
    os.makedirs(subtitle_output_dir, exist_ok=True)

    # Step 1: 用FFprobe检测字幕流信息
    ffprobe_cmd = [
        ffprobe_exe_path, "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index,codec_name:stream_tags=language",
        "-of", "json",
        source_video_path
    ]

    # 执行探测命令
    result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
    streams_info = json.loads(result.stdout)

    # Step 2: 遍历所有字幕流
    for stream in streams_info.get("streams", []):
        index = stream["index"]
        codec = stream.get("codec_name", "unknown")
        lang = stream.get("tags", {}).get("language", "und")

        # 确定输出格式（优先保留原始格式）
        ext_map = {
            "subrip": "srt",
            "ass": "ass",
            "webvtt": "vtt",
            "mov_text": "srt"
        }
        # 默认转为SRT
        ext = ext_map.get(codec, "srt")

        # 构造字幕文件输出路径
        output_path = os.path.join(
            subtitle_output_dir,
            f"{source_video_filename}_{index}_{lang}.{ext}"
        )

        # Step 3: 提取单个字幕流
        if video_file_suffix == "mkv":
            ffmpeg_cmd = [
                ffmpeg_exe_path, "-i", source_video_path,
                "-map", f"0:{index}",
                "-c", "copy",
                "-y", output_path
            ]
        else:
            ffmpeg_cmd = [
                ffmpeg_exe_path, "-i", source_video_path,
                "-map", f"0:{index}",
                "-c:s", "srt",
                "-f", "srt",
                "-y", output_path
            ]

        extract_result = True
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            print(f"成功提取字幕流 {index} ({lang}) 到 {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"提取字幕流 {index} 失败: {e.stderr}")
            extract_result = False
        finally:
            return extract_result

"""
提取视频文件中内嵌的软字幕
"""
if __name__ == '__main__':
    ffmpeg_basepath = "D:/ffmpeg-5.1.2/"
    source_video_path = "E:/BadiduNetDiskDownload/test/功夫01.mov"
    subtitle_output_dir = "E:/BadiduNetDiskDownload/output/subtitle/"
    extract_soft_subtitles(source_video_path, ffmpeg_basepath, subtitle_output_dir=subtitle_output_dir)
