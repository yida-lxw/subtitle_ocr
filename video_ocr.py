#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.14 18:23
# @Author  : yida
# @File    : video_ocr.py
# @Software: PyCharm
from config.app_config import APPConfig
from db_pool import SQLTemplate
from image_ocr import ImageOCR
from thread_pool.thread_pool_manager import ThreadPoolManager
from utils.file_utils import FileUtils
from utils.string_utils import StringUtils
from video_frame_extractor import VideoFrameExtractor


class VideoOcr:
    def __init__(self, video_file_path, task_id:str, file_hash:str,app_config: APPConfig, sql_template: SQLTemplate,
                 thread_pool_manager: ThreadPoolManager):
        self.video_file_path = video_file_path
        self.video_file_name = FileUtils.get_filename_without_suffix(video_file_path)
        self.task_id = task_id
        self.app_config = app_config
        self.sql_template = sql_template
        self.thread_pool_manager = thread_pool_manager
        # 获取文件的MD5摘要
        #self.file_hash = FileUtils.get_md5_of_file(video_file_path)
        self.file_hash = file_hash
        self.work_dir = app_config.work_dir
        self.work_dir = StringUtils.replaceBackSlash(self.work_dir)
        self.work_dir = StringUtils.to_ends_with_back_slash(self.work_dir)
        self.extracted_frames_relative_dir = app_config.extracted_frames_relative_dir
        self.source_image_parent_path =  self.work_dir + self.extracted_frames_relative_dir + "/" + self.video_file_name
        self.video_frame_extractor = VideoFrameExtractor(video_file_path=self.video_file_path, word_dir=self.work_dir,
                                                         extracted_frames_relative_dir=self.app_config.extracted_frames_relative_dir,
                                                         ffmpeg_path=self.app_config.ffmpeg_path)

        self.image_ocr = ImageOCR(video_file_name=self.video_file_name,source_image_parent_path=self.source_image_parent_path,
                                  file_hash=self.file_hash,task_id=self.task_id,image_total_count=0, app_config=self.app_config,
                                  sql_template=self.sql_template, thread_pool_manager=self.thread_pool_manager)

    def ocr_video(self):
        self.video_frame_extractor.extract_frames()
        image_total_count = self.video_frame_extractor.get_image_total_count()
        self.image_ocr.set_image_total_count(image_total_count)
        self.image_ocr.ocr_image()
