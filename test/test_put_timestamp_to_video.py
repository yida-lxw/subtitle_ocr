#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.02 14:24
# @Author  : yida
# @File    : test_put_timestamp_to_video.py
# @Software: PyCharm
from utils.file_utils import FileUtils
from utils.video_utils import VideoUtils

if __name__ == '__main__':
    ffmpeg_path = "D:/ffmpeg-20250401/bin/ffmpeg.exe"
    vide_file_parent_folder = "D:/tmp/source_videos/"
    jpg_file_output_path = "D:/tmp/jpg_with_timestamp/"
    video_file_list = FileUtils.get_subfiles_in_folder(vide_file_parent_folder)
    fps = "2"
    for video_file_path in video_file_list:
        result = VideoUtils.put_timestamp_to_video(video_file_path, jpg_file_output_path, ffmpeg_path, fps)
        print(f"视频文件{video_file_path}转成图片:{result}")
