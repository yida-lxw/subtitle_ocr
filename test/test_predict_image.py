#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.12 11:50
# @Author  : yida
# @File    : test_predict_image.py
# @Software: PyCharm

import os

from config.app_config import APPConfig
from predict_image import predict_image_execute
from utils.file_utils import FileUtils
from utils.image_utils import ImageUtils
from utils.string_utils import StringUtils
from utils.ocr_utils import PaddleOCRUtils
from extract_timestamp import determin_timestamp_by_file_name

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

app_config_path = "config/app.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)

if __name__ == '__main__':
    source_image_file_path = "D:/test_00000056_56.jpg"
    source_image_filename = FileUtils.get_filename_without_suffix(source_image_file_path)
    output_predict_image = True
    delete_original_image_after_predict = False
    predict_flag, predict_data = predict_image_execute(source_image_file_path, output_predict_image, delete_original_image_after_predict)
    predict_flag_text = "成功" if predict_flag else "失败"
    print(f"对图片{source_image_file_path}文件进行模型推理, 执行{predict_flag_text}")
    if predict_flag:
        predict_data_json = StringUtils.to_json_str(predict_data)
        print(predict_data_json)

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
        if is_valid_predict_bbox:
            work_dir = app_config_loaded.work_dir
            work_dir = StringUtils.replaceBackSlash(work_dir)
            work_dir = StringUtils.to_ends_with_back_slash(work_dir)
            croped_images_relative_dir = app_config_loaded.croped_images_relative_dir
            crop_image_save_dir = work_dir + croped_images_relative_dir + "/"
            crop_result, save_image_file_path = ImageUtils.crop_bbox_images(source_image_file_path, bbox, crop_image_save_dir)
            if crop_result:
                print(f"裁剪图片成功, 裁剪后的图片文件路径为: {save_image_file_path}")
                # 开始对图片进行OCR
                ocr_flag, ocr_data = PaddleOCRUtils.image_ocr(save_image_file_path)
                ocr_flag_text = "识别成功" if ocr_flag else "识别失败"
                print(f"裁剪的图片{save_image_file_path}OCR{ocr_flag_text}")
                if ocr_flag:
                    ocr_data_json = StringUtils.to_json_str(ocr_data)
                    print(f"识别结果:\n{ocr_data_json}")
                    (hour, min, second, million_second) = determin_timestamp_by_file_name(source_image_filename)
                    hour_str = StringUtils.left_pad_zero(hour, total_len=2)
                    min_str = StringUtils.left_pad_zero(min, total_len=2)
                    second_str = StringUtils.left_pad_zero(second, total_len=2)
                    million_second_str = StringUtils.left_pad_zero(million_second, total_len=3)
                    frame_time = f"{hour_str}:{min_str}:{second_str},{million_second_str}"
                    print(f"当前帧对应时间戳:{frame_time}")
                    # 开始将字幕数据写入SQLLite中

