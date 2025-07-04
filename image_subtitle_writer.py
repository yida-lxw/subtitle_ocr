#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.14 15:31
# @Author  : yida
# @File    : image_subtitle_writer.py
# @Software: PyCharm
from config.app_config import APPConfig
from db_pool import SQLTemplate
from utils.string_utils import StringUtils

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

# 加载配置文件
app_config_path = "config/app.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)
table_name = app_config_loaded.image_subtitle_ocr_table_name

create_table_sql_tpl = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id  TEXT NOT NULL,
            score DECIMAL(18,17) NOT NULL,
            frame_time  TEXT NOT NULL,
            frame_index  INTEGER NOT NULL,
            ocr_result  TEXT NOT NULL,
            subtitle  TEXT NOT NULL,
            file_hash  TEXT NOT NULL,
            file_name  TEXT NOT NULL,
            image_total_count INTEGER NOT NULL
        );
    """

select_sql = f"SELECT * FROM {table_name} WHERE file_hash = ? and frame_index = ?"
insert_sql = f"INSERT OR IGNORE INTO {table_name}(task_id, score, frame_time, frame_index, ocr_result, subtitle, file_hash, file_name,image_total_count) VALUES (?,?,?,?,?,?,?,?,?)"
update_sql = f"UPDATE {table_name} SET score=?, frame_time=?,frame_index=?, ocr_result=?,subtitle=?,file_name=? WHERE file_hash=?"

class ImageSubtitleOCRInfo:
    def __init__(self, ocr_result: str, subtitle:str, score:float, frame_time:str, frame_index:int, task_id:str,
                 file_hash:str, file_name:str, image_total_count:int):
        self.ocr_result = ocr_result
        self.subtitle = subtitle
        self.score = score
        self.frame_time = frame_time
        self.frame_index = frame_index
        self.task_id = task_id
        self.file_hash = file_hash
        self.file_name = file_name
        self.image_total_count = image_total_count

class ImageSubtitleWriter:

    def __init__(self, sql_template: SQLTemplate):
        self.sql_template = sql_template

    def create_table(self):
        create_table_sql = create_table_sql_tpl.replace("${table_name}", table_name)
        create_result = self.sql_template.create_table(create_table_sql)
        create_result_text = "成功" if create_result else "失败"
        print(f"SQLLite表{table_name}创建{create_result_text}")

    def save_ocr_result(self, image_subtitle_ocr_info: ImageSubtitleOCRInfo) -> bool:
        if image_subtitle_ocr_info is None:
            return False
        ocr_result = image_subtitle_ocr_info.ocr_result
        subtitle = image_subtitle_ocr_info.subtitle
        score = image_subtitle_ocr_info.score
        frame_time = image_subtitle_ocr_info.frame_time
        frame_index = image_subtitle_ocr_info.frame_index
        task_id = image_subtitle_ocr_info.task_id
        file_hash = image_subtitle_ocr_info.file_hash
        file_name = image_subtitle_ocr_info.file_name
        image_total_count = image_subtitle_ocr_info.image_total_count
        subtitle_ocr_result = self.sql_template.find_one(select_sql, (file_hash,frame_index))
        if subtitle_ocr_result is None or len(subtitle_ocr_result) <= 0:
            effect_row = self.sql_template.insert(insert_sql, return_id=False, args=(task_id, score, frame_time, frame_index,
                                                                        ocr_result, subtitle, file_hash, file_name,image_total_count))
        else:
            effect_row = self.sql_template.update(update_sql, args=(score, frame_time,frame_index, ocr_result,
                                                                    subtitle, file_name, file_hash))
        return effect_row > 0

    # 加载每张图片OCR成功的字幕数据
    def load_ocr_success_of_image_subtitle(self, frame_index_list:list, file_hash:str):
        frame_index_size = len(frame_index_list)
        frame_index_list_str = ""
        for index in range(frame_index_size):
            if index == 0:
                frame_index_list_str += "?"
            else:
                frame_index_list_str += ",?"

        query_params = tuple(frame_index_list)
        query_params = query_params.__add__((file_hash, ))
        query_sql = f"SELECT * FROM {table_name} WHERE frame_index in ({frame_index_list_str}) and file_hash=? order by frame_index"
        return self.sql_template.find_many(query_sql, args=query_params)








