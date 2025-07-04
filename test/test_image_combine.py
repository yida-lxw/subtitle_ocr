#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.03 11:46
# @Author  : yida
# @File    : test_image_combine.py
# @Software: PyCharm
import os
from pathlib import Path

from utils.string_utils import StringUtils
from utils.file_utils import FileUtils

# 将缩放后的图片合并到一个文件夹中
if __name__ == '__main__':
    source_images_dir = "D:/tmp/jpg_resize/"
    dest_images_dir = "D:/tmp/jpg_resize_combine/"
    if not os.path.exists(dest_images_dir):
        os.makedirs(dest_images_dir)

    for subdir in Path(source_images_dir).iterdir():
        if subdir.is_dir():
            sub_dir_name = subdir.name
            sub_dir_abspath = str(subdir.resolve())
            sub_dir_abspath = StringUtils.replaceBackSlash(sub_dir_abspath)
            sub_dir_abspath = StringUtils.to_ends_with_back_slash(sub_dir_abspath)
            sub_file_list = FileUtils.get_subfiles_in_folder(sub_dir_abspath)
            if sub_file_list is None or len(sub_file_list) <= 0:
                continue
            for sub_file_path in sub_file_list:
                sub_file_path = StringUtils.replaceBackSlash(sub_file_path)
                sub_file_name = FileUtils.get_filename_with_suffix(sub_file_path)
                dest_image_path = dest_images_dir + sub_file_name
                FileUtils.copy_file(sub_file_path, dest_image_path)