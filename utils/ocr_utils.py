#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.12 13:29
# @Author  : yida
# @File    : ocr_utils.py
# @Software: PyCharm

from paddleocr import PaddleOCR

from config.app_config import APPConfig
from utils.file_utils import FileUtils
from utils.string_utils import StringUtils
from text_translator import traditional_to_simple_with_text

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

app_config_path = "config/app.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)

ocr = PaddleOCR(use_gpu=True, use_angle_cls=app_config_loaded.ocr_auto_rotate_image, lang=app_config_loaded.ocr_language)

class PaddleOCRUtils:

    @staticmethod
    def image_ocr2(image_file_path:str):
        image_file_path = StringUtils.replaceBackSlash(image_file_path)
        try:
            result = ocr.ocr(image_file_path, cls=True)
        except:
            return False, {}

        final_ocr_result = {}
        if result is None or result[0] is None:
            return True, final_ocr_result
        index = 0
        doc_list = []
        for line in result:
            for detection in line:
                text = detection[1][0]
                if text is None or len(text) <= 0:
                    index += 1
                    continue
                if StringUtils.has_traditional_by_unicode(text):
                    text = traditional_to_simple_with_text(text)

                if index % 3 == 0:
                    current_doc = {}
                    current_doc["name"] = text
                elif index % 3 == 1:
                    current_doc["phone_number"] = text
                elif index % 3 == 2:
                    current_doc["money"] = text
                    doc_list.append(current_doc)
                index += 1
        return True, doc_list


    @staticmethod
    def image_ocr(image_file_path:str):
        image_file_path = StringUtils.replaceBackSlash(image_file_path)
        original_filename = FileUtils.get_filename_without_suffix(image_file_path)
        try:
            result = ocr.ocr(image_file_path, cls=True)
        except:
            return False, {}

        final_ocr_result = {}
        if result is None or result[0] is None:
            return True, final_ocr_result
        max_score = 0.0
        for line in result:
            for detection in line:
                # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                # 标注框的4个顶点的(x,y)坐标,单位:像素,四个顶点按顺时针顺序排列
                boxes = detection[0]
                text = detection[1][0]
                if text is None or len(text) <= 0:
                    continue
                if StringUtils.has_traditional_by_unicode(text):
                    text = traditional_to_simple_with_text(text)
                score = detection[1][1]
                print(f"texts:{text} --> boxes:{boxes},scores:{score}")
                if score > max_score:
                    max_score = score
                    final_ocr_result = {
                        "file_path": image_file_path,
                        "file_name": original_filename,
                        "text": text,
                        "score": score,
                        "boxes": boxes
                    }
        if max_score <= 0.0 or len(final_ocr_result) <= 0:
            return True, {}
        else:
            return True, final_ocr_result
