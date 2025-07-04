#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.14 17:05
# @Author  : yida
# @File    : image_ocr.py
# @Software: PyCharm
import asyncio
from asyncio import as_completed, wrap_future
from time import sleep

from db_pool import SQLTemplate
from image_ocr_result_merger import ImageOcrResultMerger, VideoOcrInfo
from ocr_status_writer import SubtitleOCRStatusWriter, SubtitleOCRStatusInfo
from predict_image import predict_image_execute
from srt_correct import subtitle_correct
from status_constants import save_image_subtitle_ocr_success, save_image_subtitle_ocr_failed, \
    image_subtitle_area_predict_failed, image_subtitle_area_predict_box_invalid, image_subtitle_area_croped_failed, \
    image_subtitle_ocr_failed, image_subtitle_ocr_no_data, save_video_subtitle_success
from image_subtitle_writer import ImageSubtitleWriter, ImageSubtitleOCRInfo
from thread_pool.thread_pool_manager import ThreadPoolManager
from utils.file_utils import FileUtils
from utils.image_utils import ImageUtils
from utils.logger import setup_logger
from utils.string_utils import StringUtils
from utils.ocr_utils import PaddleOCRUtils
from extract_timestamp import determin_timestamp_by_file_name, determin_sequence_no, determin_timestamp_by_sequnce_num
from video_subtitle_merge_status_writer import VideoSubtitleMergeStatusMerger, VideoSubtitleMergeStatusInfo

logger = setup_logger('image_ocr')

class ImageOCR:
    def __init__(self, video_file_name:str,source_image_parent_path, file_hash:str, task_id:str, image_total_count:int, app_config, sql_template: SQLTemplate,
                 thread_pool_manager: ThreadPoolManager):
        self.video_file_name = video_file_name
        self.source_image_parent_path = source_image_parent_path
        self.file_hash = file_hash
        self.task_id = task_id
        self.image_total_count = image_total_count
        self.app_config = app_config
        work_dir = app_config.work_dir
        work_dir = StringUtils.replaceBackSlash(work_dir)
        work_dir = StringUtils.to_ends_with_back_slash(work_dir)
        self.work_dir = work_dir
        self.sql_template = sql_template
        self.image_subtitle_writer = ImageSubtitleWriter(sql_template)
        self.subtitle_ocr_status_writer = SubtitleOCRStatusWriter(sql_template,self.file_hash, self.image_total_count)
        self.image_ocr_result_merger = ImageOcrResultMerger(file_hash, task_id, image_total_count, app_config, self.image_subtitle_writer,
                                                            self.subtitle_ocr_status_writer, sql_template)

        self.video_subtitle_merge_status_merger = VideoSubtitleMergeStatusMerger(self.file_hash, app_config, sql_template)
        self.source_image_file_list = None
        self.thread_pool_manager = thread_pool_manager


    def ocr_image(self):
        logger.info("enter ocr_image function")
        self.source_image_file_list = FileUtils.get_subfiles_in_folder(self.source_image_parent_path)
        image_file_count = self.image_total_count
        if image_file_count <= 0:
            print(f"文件夹{self.source_image_parent_path}下没有图片文件")
            return
        image_total_count = len(self.source_image_file_list)

        #loop = asyncio.get_event_loop()
        #tasks = []
        for source_image_file_path in self.source_image_file_list:
            file_suffix = FileUtils.get_suffix(source_image_file_path).lower()
            if file_suffix not in ["jpg", "jpeg", "png"]:
                continue

            # logger.info(f"submit image ocr task, source_image_file_path:{source_image_file_path}, image_total_count:{image_total_count}")
            # task = loop.run_in_executor(None, self.ocr_pre_image, source_image_file_path, image_total_count)
            # tasks.append(task)
            self.ocr_pre_image(source_image_file_path, image_total_count)

        # 等待所有任务完成
        #await asyncio.gather(*tasks)

        is_complete = self.subtitle_ocr_status_writer.is_all_complete()
        if not is_complete:
            print("图片ocr并没有全部完成, 可能存在部分图片字幕区域预测失败或字幕区域预测框不合法或字幕区域裁剪失败")
            return
        else:
            print("所有图片ocr已完成, 开始进行字幕识别结果合并")
            merged_subtitle_list = self.image_ocr_result_merger.merge_ocr_result()
            if merged_subtitle_list is None or not merged_subtitle_list:
                print("字幕识别结果合并失败")
                return
            subtitle_json = StringUtils.to_json_str(merged_subtitle_list)
            for subtitle_ocr_info in merged_subtitle_list:
                subtitle_ocr_info["error_status"] = ""
                subtitle_ocr_info["progress"] = save_video_subtitle_success
                video_subtitle_info = VideoOcrInfo(self.task_id, subtitle_json,
                                                           self.file_hash,
                                                           self.video_file_name,
                                                           subtitle_ocr_info["error_status"],
                                                           save_video_subtitle_success
                                                           )
                try:
                    self.image_ocr_result_merger.save_video_ocr_result(video_subtitle_info)
                except BaseException as ex:
                    logger.error(ex)
            video_subtitle_merge_status_info = VideoSubtitleMergeStatusInfo(self.file_hash,
                                                                            self.video_file_name, "ready_for_subtitle_extraction")
            self.video_subtitle_merge_status_merger.save_video_subtitle_merge_status_result(video_subtitle_merge_status_info)





    def ocr_pre_image(self, source_image_file_path:str, image_total_count:int):
        print(f"开始执行ocr_pre_image:[{source_image_file_path}]")
        source_image_filename = FileUtils.get_filename_without_suffix(source_image_file_path)
        output_predict_image = self.app_config.output_predict_image
        delete_original_image_after_predict = self.app_config.delete_original_image_after_predict
        predict_flag, predict_data = predict_image_execute(source_image_file_path, output_predict_image,
                                                           delete_original_image_after_predict)
        predict_flag_text = "成功" if predict_flag else "失败"
        print(f"对图片{source_image_file_path}文件进行模型推理, 执行{predict_flag_text}")
        frame_index = determin_sequence_no(source_image_filename)
        frame_time = determin_timestamp_by_sequnce_num(frame_index)
        hour, min, second, million_second = frame_time
        hour_str = StringUtils.left_pad_zero(hour, 2)
        min_str = StringUtils.left_pad_zero(min, 2)
        second_str = StringUtils.left_pad_zero(second, 2)
        million_second_str = StringUtils.left_pad_zero(million_second, 3)
        frame_time_str = f"{hour_str}:{min_str}:{second_str},{million_second_str}"
        if not predict_flag or (predict_data is None or len(predict_data) <= 0):
            ocr_status = image_subtitle_area_predict_failed
            subtitle_ocr_status_info = SubtitleOCRStatusInfo(self.task_id,frame_time_str,frame_index, ocr_status,
                                                             self.file_hash, source_image_filename,image_total_count)
            self.subtitle_ocr_status_writer.save_ocr_status_result(subtitle_ocr_status_info)
        else:
            image_width, image_height = ImageUtils.get_image_size(source_image_file_path)
            xywh = predict_data["xywh"]
            x_center = xywh[0]
            y_center = xywh[1]
            w = xywh[2]
            h = xywh[3]
            x = x_center - w / 2
            y = y_center - h / 2
            bbox = (x, y, w, h)

            # 判断检测框是否合法
            is_valid_predict_bbox = ImageUtils.is_valid_bbox(image_width, image_height, x, y, w, h)
            print("检测框是否合法:", is_valid_predict_bbox)
            if not is_valid_predict_bbox:
                ocr_status = image_subtitle_area_predict_box_invalid
                subtitle_ocr_status_info = SubtitleOCRStatusInfo(self.task_id, frame_time_str, frame_index, ocr_status,
                                                                 self.file_hash, source_image_filename,
                                                                 image_total_count)
                self.subtitle_ocr_status_writer.save_ocr_status_result(subtitle_ocr_status_info)
            else:
                croped_images_relative_dir = self.app_config.croped_images_relative_dir
                crop_image_save_dir = self.work_dir + croped_images_relative_dir + "/"
                crop_result, save_image_file_path = ImageUtils.crop_bbox_images(source_image_file_path, bbox,
                                                                                crop_image_save_dir)
                if not crop_result:
                    ocr_status = image_subtitle_area_croped_failed
                    subtitle_ocr_status_info = SubtitleOCRStatusInfo(self.task_id, frame_time_str, frame_index, ocr_status,
                                                                     self.file_hash, source_image_filename,
                                                                     image_total_count)
                    self.subtitle_ocr_status_writer.save_ocr_status_result(subtitle_ocr_status_info)
                else:
                    print(f"裁剪图片成功, 裁剪后的图片文件路径为: {save_image_file_path}")
                    # 开始对图片进行OCR
                    ocr_flag, ocr_data = PaddleOCRUtils.image_ocr(save_image_file_path)
                    ocr_flag_text = "识别成功" if ocr_flag else "识别失败"
                    print(f"裁剪的图片{save_image_file_path}OCR{ocr_flag_text}")
                    if not ocr_flag:
                        ocr_status = image_subtitle_ocr_failed
                        subtitle_ocr_status_info = SubtitleOCRStatusInfo(self.task_id, frame_time_str, frame_index,
                                                                         ocr_status,
                                                                         self.file_hash, source_image_filename,
                                                                         image_total_count)
                        self.subtitle_ocr_status_writer.save_ocr_status_result(subtitle_ocr_status_info)
                    else:
                        if ocr_data is None or len(ocr_data) <= 0:
                            ocr_status = image_subtitle_ocr_no_data
                            subtitle_ocr_status_info = SubtitleOCRStatusInfo(self.task_id, frame_time_str, frame_index,
                                                                             ocr_status,
                                                                             self.file_hash, source_image_filename,
                                                                             image_total_count)
                            self.subtitle_ocr_status_writer.save_ocr_status_result(subtitle_ocr_status_info)
                        else:
                            ocr_data_json = StringUtils.to_json_str(ocr_data)
                            print(f"识别结果:\n{ocr_data_json}")
                            (hour, min, second, million_second) = determin_timestamp_by_file_name(source_image_filename)
                            hour_str = StringUtils.left_pad_zero(hour, total_len=2)
                            min_str = StringUtils.left_pad_zero(min, total_len=2)
                            second_str = StringUtils.left_pad_zero(second, total_len=2)
                            million_second_str = StringUtils.left_pad_zero(million_second, total_len=3)
                            frame_time_text = f"{hour_str}:{min_str}:{second_str},{million_second_str}"
                            print(f"当前帧对应时间戳:{frame_time_text}")
                            # 开始将字幕数据写入SQLLite中
                            ocr_result = StringUtils.to_json_str(ocr_data)
                            subtitle = ocr_data["text"]
                            score = ocr_data["score"]

                            # 字幕文本错别字矫正
                            #subtitle = subtitle_correct(subtitle, self.app_config)

                            image_subtitle_ocr_info = ImageSubtitleOCRInfo(ocr_result, subtitle, score, frame_time_text, frame_index,
                                                                   self.task_id, self.file_hash, source_image_filename,
                                                                   image_total_count)
                            save_result = self.image_subtitle_writer.save_ocr_result(
                                image_subtitle_ocr_info=image_subtitle_ocr_info)
                            # 这里需要将每一张图片的识别结果状态保存到SQLLite
                            ocr_status = save_image_subtitle_ocr_success if save_result else save_image_subtitle_ocr_failed
                            subtitleOcrStatusInfo = SubtitleOCRStatusInfo(self.task_id, frame_time_text, frame_index, ocr_status,
                                                                          self.file_hash, source_image_filename,
                                                                          image_total_count)
                            ocr_status_save_result = self.subtitle_ocr_status_writer.save_ocr_status_result(
                                subtitleOcrStatusInfo=subtitleOcrStatusInfo)
                            print(f"保存ocr识别执行状态:{ocr_status_save_result}")



    def set_image_total_count(self, image_total_count: int):
        self.image_total_count = image_total_count
        self.subtitle_ocr_status_writer.image_total_count = image_total_count
        self.image_ocr_result_merger.image_total_count = image_total_count