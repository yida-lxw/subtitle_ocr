#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.14 19:05
# @Author  : yida
# @File    : image_ocr_result_merger.py
# @Software: PyCharm
from config.app_config import APPConfig
from ocr_status_writer import SubtitleOCRStatusWriter
from image_subtitle_writer import ImageSubtitleWriter
from status_constants import save_video_subtitle_success
from utils.object_utils import ObjectUtils
from utils.string_utils import StringUtils
from db_pool import SQLTemplate

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

# 加载配置文件
app_config_path = "config/app.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)
table_name = app_config_loaded.video_subtitle_merge_table_name

create_table_sql_tpl = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash  TEXT NOT NULL,
            file_name  TEXT NOT NULL,
            progress TXT
        );
    """

select_sql = f"SELECT * FROM {table_name} WHERE file_hash = ?"
insert_sql = f"INSERT OR IGNORE INTO {table_name}(file_hash,file_name, progress) VALUES (?,?,?)"
update_sql = f"UPDATE {table_name} SET file_name=?,progress=? WHERE file_hash=?"

class VideoSubtitleMergeStatusInfo:
    def __init__(self, file_hash:str, file_name:str, progress:str):
        self.file_hash = file_hash
        self.file_name = file_name
        self.progress = progress

class VideoSubtitleMergeStatusMerger:
    def __init__(self, file_hash:str, app_config, sql_template: SQLTemplate):
        self.file_hash = file_hash
        self.app_config = app_config
        self.sql_template = sql_template

    def create_table(self):
        create_table_sql = create_table_sql_tpl.replace("${table_name}", table_name)
        create_result = self.sql_template.create_table(create_table_sql)
        create_result_text = "成功" if create_result else "失败"
        print(f"SQLLite表{table_name}创建{create_result_text}")

    def save_video_subtitle_merge_status_result(self, video_subtitle_merge_status_info: VideoSubtitleMergeStatusInfo) -> bool:
        if video_subtitle_merge_status_info is None:
            return False
        file_hash = video_subtitle_merge_status_info.file_hash
        file_name = video_subtitle_merge_status_info.file_name
        progress = video_subtitle_merge_status_info.progress
        video_subtitle_merge_status_result = self.sql_template.find_one(select_sql, (file_hash,))
        if video_subtitle_merge_status_result is None or len(video_subtitle_merge_status_result) <= 0:
            effect_row = self.sql_template.insert(insert_sql, return_id=False, args=(file_hash,file_name,progress))
        else:
            effect_row = self.sql_template.update(update_sql, args=(file_name, progress, file_hash,))
        return effect_row > 0

    # 批量保存视频OCR结果状态数据
    def batch_save_video_subtitle_merge_status_result(self, video_subtitle_merge_status_info_list: list) -> bool:
        if video_subtitle_merge_status_info_list is None or len(video_subtitle_merge_status_info_list) <= 0:
            return False
        effect_row = self.sql_template.batch_insert(insert_sql, args_list=video_subtitle_merge_status_info_list)
        return effect_row > 0


    # 判断视频的字幕数据已经就绪
    def is_subtitle_ready(self):
        query_count_sql = f"SELECT COUNT(*) FROM {table_name} WHERE file_hash = ? and progress='ready_for_subtitle_extraction'"
        matched_count = self.sql_template.query_count(query_count_sql, args=(self.file_hash,))
        return matched_count > 0









