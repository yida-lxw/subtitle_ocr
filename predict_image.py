#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.12 11:33
# @Author  : yida
# @File    : predict_image.py
# @Software: PyCharm

import os
from ultralytics import YOLO

from config.app_config import APPConfig
from utils.file_utils import FileUtils
from utils.image_utils import ImageUtils
from utils.string_utils import StringUtils

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

app_config_path = "config/app.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)


# 加载模型
model_path = app_config_loaded.model_path
model = YOLO(model_path)

# 对给定图片进行模型推理
def predict_image_execute(image_file_path: str, output_predict_image: bool = app_config_loaded.output_predict_image,
                          delete_original_image_after_predict: bool = app_config_loaded.delete_original_image_after_predict):
    try:
        image_file_path = StringUtils.replaceBackSlash(image_file_path)
        orignal_filename = FileUtils.get_filename_with_suffix(image_file_path)
        file_suffix = FileUtils.get_file_suffix(orignal_filename)
        if file_suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            return False, {}
        predict_data = {}
        (image_width, image_height) = ImageUtils.get_image_size(image_file_path)
        predict_results = model.predict(image_file_path, augment=False, imgsz=(image_width, image_height), save=output_predict_image, classes=[0])
        if predict_results is None or len(predict_results) <= 0:
            predict_flag = False
            predict_data = {
                "file_name": orignal_filename,
                "file_path": image_file_path,
                "predict_flag": predict_flag,
                "score": 0.0,
                "xywh": None,
                "class_name": ""
            }
        else:
            max_score = 0.0
            max_predict_data = {}
            for predict_result in predict_results:
                boxes = predict_result.boxes
                if boxes is None or len(boxes) <= 0:
                    continue
                predict_flag = True
                current_predict_data = {}
                current_predict_data["file_name"] = orignal_filename
                current_predict_data["file_path"] = image_file_path
                current_predict_data["predict_flag"] = predict_flag
                class_name = predict_result.names[0]
                current_predict_data["class_name"] = class_name
                score: float = float(boxes.conf.tolist()[0])
                min_score = app_config_loaded.predict_min_score
                if score < min_score:
                    print(f"图片{orignal_filename}的字幕区域预测置信度{score}小于最小置信度{min_score}, 忽略该图片")
                    continue
                current_predict_data["score"] = score
                xywh = boxes.xywh.tolist()
                current_predict_data["xywh"] = xywh[0]
                if score > max_score:
                    max_score = score
                    max_predict_data = current_predict_data
            if max_score == 0.0 or len(max_predict_data) <= 0:
                predict_flag = False
                predict_data["file_name"] = orignal_filename
                predict_data["file_path"] = image_file_path
                predict_data["predict_flag"] = predict_flag
                predict_data["score"] = 0.0
                predict_data["xywh"] = [],
                predict_data["class_name"] = ""
            else:
                predict_data = max_predict_data
                predict_flag = (predict_data is not None and len(predict_data) > 0)

        if delete_original_image_after_predict:
            FileUtils.deleteFileIfExists(image_file_path)
        return predict_flag, predict_data
    except Exception:
        return False, {}
