#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.03 11:46
# @Author  : yida
# @File    : test_paddle_ocr.py
# @Software: PyCharm

from utils.ocr_utils import PaddleOCRUtils
from utils.string_utils import StringUtils

if __name__ == '__main__':
    image_file_path = 'D:/tmp/label_images/images/3分钟揭示哭声_00000358.jpg'
    ocr_flag, ocr_data = PaddleOCRUtils.image_ocr(image_file_path)
    ocr_flag_text = "识别成功" if ocr_flag else "识别失败"
    print(f"图片{image_file_path}OCR{ocr_flag_text}")
    if ocr_flag:
        ocr_data_json = StringUtils.to_json_str(ocr_data)
        print(f"识别结果:\n{ocr_data_json}")



