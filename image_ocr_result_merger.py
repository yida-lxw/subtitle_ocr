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
table_name = app_config_loaded.video_hard_subtitle_ocr_table_name

create_table_sql_tpl = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id  TEXT NOT NULL,
            subtitle  TEXT NOT NULL,
            file_hash  TEXT NOT NULL,
            file_name  TEXT NOT NULL,
            error_status TEXT,
            progress TXT
        );
    """

select_sql = f"SELECT * FROM {table_name} WHERE file_hash = ?"
insert_sql = f"INSERT OR IGNORE INTO {table_name}(task_id,subtitle,file_hash,file_name,error_status, progress) VALUES (?,?,?,?,?,?)"
update_sql = f"UPDATE {table_name} SET subtitle=?,error_status=?,progress=? WHERE file_hash=?"
update_error_progress_sql = f"UPDATE {table_name} SET error_status=?,progress=? WHERE file_hash=?"

class VideoOcrInfo:
    def __init__(self, task_id:str, subtitle:str,file_hash:str, file_name:str, error_status:str, progress:str):
        self.task_id = task_id
        self.subtitle = subtitle
        self.file_hash = file_hash
        self.file_name = file_name
        self.error_status = error_status
        self.progress = progress

class ImageOcrResultMerger:
    def __init__(self, file_hash:str, task_id:str, image_total_count:int, app_config, image_subtitle_writer: ImageSubtitleWriter,
                 subtitle_ocr_status_writer: SubtitleOCRStatusWriter, sql_template: SQLTemplate):
        self.file_hash = file_hash
        self.task_id = task_id
        self.image_total_count = image_total_count
        self.app_config = app_config
        self.image_subtitle_writer = image_subtitle_writer
        self.subtitle_ocr_status_writer = subtitle_ocr_status_writer
        self.sql_template = sql_template

    def create_table(self):
        create_table_sql = create_table_sql_tpl.replace("${table_name}", table_name)
        create_result = self.sql_template.create_table(create_table_sql)
        create_result_text = "成功" if create_result else "失败"
        print(f"SQLLite表{table_name}创建{create_result_text}")

    def save_video_ocr_result(self, video_ocr_info: VideoOcrInfo) -> bool:
        if video_ocr_info is None:
            return False
        task_id = video_ocr_info.task_id
        subtitle = video_ocr_info.subtitle
        file_hash = video_ocr_info.file_hash
        file_name = video_ocr_info.file_name
        error_status = video_ocr_info.error_status
        progress = video_ocr_info.progress
        subtitle_ocr_result = self.sql_template.find_one(select_sql, (file_hash,))
        if subtitle_ocr_result is None or len(subtitle_ocr_result) <= 0:
            effect_row = self.sql_template.insert(insert_sql, return_id=False, args=(task_id, subtitle,file_hash,file_name,
                                                                                     error_status,progress))
        else:
            effect_row = self.sql_template.update(update_sql, args=(subtitle,error_status, progress, file_hash))
        return effect_row > 0

    # 批量保存视频OCR结果
    def batch_save_video_ocr_result(self, video_ocr_info_list: list) -> bool:
        if video_ocr_info_list is None or len(video_ocr_info_list) <= 0:
            return False
        effect_row = self.sql_template.batch_insert(insert_sql, args_list=video_ocr_info_list)
        return effect_row > 0


    # 判断视频的字幕数据已经就绪
    def is_subtitle_ready(self):
        query_count_sql = f"SELECT COUNT(*) FROM {table_name} WHERE file_hash = ? and progress=?"
        matched_count = self.sql_template.query_count(query_count_sql, args=(self.file_hash, save_video_subtitle_success))
        return matched_count > 0



    # 合并每张图片的ocr结果
    def merge_ocr_result(self) -> list:
        if not self.subtitle_ocr_status_writer.is_all_complete():
            print("图片ocr结果尚未全部保存成功，不能执行合并")
            return False
        # 获取所有图片OCR处理成功的记录
        ocr_success_list = self.subtitle_ocr_status_writer.load_frames_for_ocr_success()
        # 获取OCR执行成功但没有字幕的帧的数量
        no_data_of_frames_count = self.subtitle_ocr_status_writer.get_no_data_of_frames_count()
        # 获取视频区域预测失败的视频帧数量
        predict_failed_frames_count = self.subtitle_ocr_status_writer.get_predict_failed_frames_count()
        # 获取视频区域预测框不合法的视频帧数量
        predict_box_invalid_frames_count = self.subtitle_ocr_status_writer.get_predict_box_invalid_frames_count()
        # 获取视频区域裁剪失败的视频帧数量
        predict_box_crop_failed_frames_count = self.subtitle_ocr_status_writer.get_predict_box_crop_failed_frames_count()

        # 获取图片OCR处理成功的记录总数
        # image_ocr_success_count = len(ocr_success_list)
        # actual_image_total_count = (image_ocr_success_count + no_data_of_frames_count + predict_failed_frames_count +
        #                             predict_box_invalid_frames_count + predict_box_crop_failed_frames_count)
        # if self.image_total_count != actual_image_total_count:
        #     print("图片OCR处理成功的记录总数与图片总数不一致，不能执行合并")
        #     return False

        frame_index_list = [ocr_success[3] for ocr_success in ocr_success_list]
        ocr_success_result_list = self.image_subtitle_writer.load_ocr_success_of_image_subtitle(frame_index_list, self.file_hash)
        merged_subtitle_list = self.deal_with_subtitle_merge(ocr_success_result_list)
        if len(merged_subtitle_list) <= 0:
            print("所有图片ocr结果合并后为空，无法执行后续操作")
            return False
        return merged_subtitle_list


    def deal_with_subtitle_merge(self, ocr_success_result_list: list):
        merged_subtitles = []
        current_start_time = None
        current_end_time = None
        current_subtitle_text = None
        current_id = 1

        # 遍历已排序的OCR结果列表
        for ocr_success_result in ocr_success_result_list:
            frame_time = ocr_success_result[3]
            subtitle_text = ocr_success_result[6]
            subtitle_text = subtitle_text.strip()

            # 初始化第一条字幕
            if current_subtitle_text is None or len(current_subtitle_text) <= 0:
                current_start_time = frame_time
                current_end_time = frame_time
                current_subtitle_text = subtitle_text
                continue

            # 当字幕内容相同且时间连续时，延长结束时间
            if subtitle_text == current_subtitle_text:
                current_end_time = frame_time
            else:
                # 保存当前合并的字幕
                merged_subtitles.append({
                    "id": current_id,
                    "time_range": f"{current_start_time} --> {current_end_time}",
                    "start_time": current_start_time,
                    "end_time": current_end_time,
                    "subtitle": current_subtitle_text
                })

                # 重置为新的字幕条目
                current_id += 1
                current_start_time = frame_time
                current_end_time = frame_time
                current_subtitle_text = subtitle_text

        # 添加最后一条字幕
        if current_subtitle_text:
            merged_subtitles.append({
                "id": current_id,
                "time_range": f"{current_start_time} --> {current_end_time}",
                "start_time": current_start_time,
                "end_time": current_end_time,
                "subtitle": current_subtitle_text
            })
        return merged_subtitles







