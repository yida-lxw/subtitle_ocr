# -*- coding: UTF-8 -*-
import os.path
from pathlib import Path
from ImageProcess import bulk_image_resize
from utils.string_utils import StringUtils

"""
测试图片缩放
"""
if __name__ == '__main__':
    source_images_dir = "D:/tmp/jpg_with_timestamp/"
    dest_images_dir = "D:/tmp/jpg_resize/"

    for subdir in Path(source_images_dir).iterdir():
        if subdir.is_dir():
            sub_dir_name = subdir.name
            sub_dir_abspath = str(subdir.resolve())
            sub_dir_abspath = StringUtils.replaceBackSlash(sub_dir_abspath)
            sub_dir_abspath = StringUtils.to_ends_with_back_slash(sub_dir_abspath)
            sub_dest_images_dir = dest_images_dir + sub_dir_name
            if not os.path.exists(sub_dest_images_dir):
                os.makedirs(sub_dest_images_dir)
            bulk_image_resize(sub_dir_abspath, sub_dest_images_dir, size=(640, 640))

