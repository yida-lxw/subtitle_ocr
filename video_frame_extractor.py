#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.14 17:05
# @Author  : yida
# @File    : video_frame_extractor.py
# @Software: PyCharm
from utils.file_utils import FileUtils
from utils.string_utils import StringUtils
from utils.video_utils import VideoUtils

# 抽取视频帧
class VideoFrameExtractor:
    def __init__(self, video_file_path, word_dir:str, extracted_frames_relative_dir, ffmpeg_path:str, fps="2", image_quality="8",
                 image_width_height:str="640x640", enable_timestamp:bool=False):
        self.video_file_path = video_file_path
        self.word_dir = word_dir
        self.extracted_frames_relative_dir = extracted_frames_relative_dir
        self.ffmpeg_path = ffmpeg_path
        self.fps = fps
        self.image_quality = image_quality
        self.image_width_height = image_width_height
        self.enable_timestamp = enable_timestamp

    def get_video_filename(self):
        video_filename = FileUtils.get_filename_without_suffix(self.video_file_path)
        return video_filename


    def get_jpg_output_path(self):
        word_dir = StringUtils.replaceBackSlash(self.word_dir)
        word_dir = StringUtils.to_ends_with_back_slash(word_dir)
        jpg_file_output_path = word_dir + self.extracted_frames_relative_dir + "/"
        return jpg_file_output_path

    def extract_frames(self) -> bool:
        jpg_output_path = self.get_jpg_output_path()
        return VideoUtils.extract_frames_from_video(self.video_file_path, jpg_output_path, self.ffmpeg_path,
                                             self.fps, self.image_quality, self.image_width_height, self.enable_timestamp)

    def get_image_total_count(self):
        jpg_output_path = self.get_jpg_output_path()
        video_file_name = self.get_video_filename()
        jpg_output_path = jpg_output_path + video_file_name + "/"
        image_file_list = FileUtils.get_file_list(jpg_output_path)
        if image_file_list is None:
            return 0
        return len(image_file_list)