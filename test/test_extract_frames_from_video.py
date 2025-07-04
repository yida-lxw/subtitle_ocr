#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.03 11:46
# @Author  : yida
# @File    : test_extract_frames_from_video.py
# @Software: PyCharm
from utils.video_utils import VideoUtils

# 从视频文件中提取视频帧
if __name__ == '__main__':
    video_path = "E:/BadiduNetDiskDownload/功夫_ass.mkv"
    jpg_file_output_path = "E:/BadiduNetDiskDownload/extract_frames/"
    ffmpeg_path = "D:/ffmpeg-20250401/bin/ffmpeg.exe"
    fps = "2"
    image_quality = "8"
    image_width_height = "640x640"
    enable_timestamp = False
    VideoUtils.extract_frames_from_video(video_path, jpg_file_output_path, ffmpeg_path, fps, image_quality,
                                         image_width_height, enable_timestamp)
