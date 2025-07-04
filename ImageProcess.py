# -*- coding: UTF-8 -*-
import os

from PIL import Image

from utils.file_utils import FileUtils
from utils.string_utils import StringUtils

'''
@Project  classified-doc-recognize 
@File     ImageProcess.py
@IDE      PyCharm 
@Desc     图片颜色黑白化并缩放成固定宽高
'''

def convert_png_to_jpg(png_image_path, jpg_image_path):
    with Image.open(png_image_path) as image:
        image.convert('RGB').save(jpg_image_path, 'JPEG', quality=100)



def bulk_image_resize(image_dir_path, output_path, size=(640, 640)):
    try:
        for root, dirs, files in os.walk(image_dir_path):
            for file in files:
                image_file_path = os.path.join(root, file)
                image_file_path = StringUtils.replaceBackSlash(image_file_path)
                orignal_filename = FileUtils.get_filename_with_suffix(image_file_path)
                file_suffix = FileUtils.get_file_suffix(orignal_filename)
                if file_suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                    print(f"只能处理图片:[{orignal_filename}]")
                    continue
                print(f"image_file_path:{image_file_path}, output_path:{output_path}")
                if not os.path.exists(image_file_path):
                    print(f"图片文件{image_file_path}不存在，无法处理，直接跳过.")
                    continue
                image_file_size = FileUtils.get_file_size(image_file_path)
                if image_file_size <= 0:
                    print(f"图片文件{image_file_path}体积为 0 bytes，无法处理，直接跳过.")
                    continue
                resize_image(image_file_path, output_path, size=size)
        return True
    except Exception as e:
        return False


def bulk_convert_to_gray_and_resize(image_dir_path, output_path, convert2gray: bool = True, resize: bool = True,
                                           size=(640, 640)):
    try:
        for root, dirs, files in os.walk(image_dir_path):
            for file in files:
                image_file_path = os.path.join(root, file)
                image_file_path = StringUtils.replaceBackSlash(image_file_path)
                orignal_filename = FileUtils.get_filename_with_suffix(image_file_path)
                file_suffix = FileUtils.get_file_suffix(orignal_filename)
                if file_suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                    print(f"只能处理图片:[{orignal_filename}]")
                    continue
                print(f"image_file_path:{image_file_path}, output_path:{output_path}")
                if not os.path.exists(image_file_path):
                    print(f"图片文件{image_file_path}不存在，无法处理，直接跳过.")
                    continue
                image_file_size = FileUtils.get_file_size(image_file_path)
                if image_file_size <= 0:
                    print(f"图片文件{image_file_path}体积为 0 bytes，无法处理，直接跳过.")
                    continue
                convert_to_black_white_and_resize(image_file_path, output_path, convert2gray=convert2gray,
                                                  resize=resize,
                                                  size=size)
        return True
    except Exception as e:
        return False

def convert_to_black_white_and_resize(image_path, output_path, convert2gray: bool=True, resize: bool=True, size=(640, 640)):
    # 打开原始图片
    with Image.open(image_path) as img:
        image_file_name = FileUtils.get_filename_with_suffix(image_path)
        if convert2gray:
            # 转换为灰度图（L模式）
            img = img.convert('L')

        if resize:
            # 缩放图片
            # img = img.resize(size, Image.ANTIALIAS)
            img = img.resize(size)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not output_path.endswith("/"):
            output_path = output_path + "/"
        # 保存处理后的图片
        output_image_file_path = output_path + image_file_name
        try:
            print(f"output_image_file_path:{output_image_file_path}")
            img.save(output_image_file_path, format="JPEG", quality=100)
            print(f"图片{image_path}已成功转换为灰色的图片{output_image_file_path}")
            return True, output_image_file_path
        except Exception as e:
            return False, image_path


def resize_image(image_path, output_path, size=(640, 640)):
    # 打开原始图片
    with Image.open(image_path) as img:
        image_file_name = FileUtils.get_filename_with_suffix(image_path)

        img = img.resize(size)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not output_path.endswith("/"):
            output_path = output_path + "/"
        # 保存处理后的图片
        output_image_file_path = output_path + image_file_name
        try:
            print(f"output_image_file_path:{output_image_file_path}")
            img.save(output_image_file_path, format="JPEG", quality=100)
            print(f"图片{image_path}已成功缩放至(640,640), 并保存至{output_image_file_path}")
            return True, output_image_file_path
        except Exception as e:
            return False, image_path


if __name__ == '__main__':
    input_image_folder_path = "G:/pdfs/original_images/"
    output_path = "G:/pdfs/output_images/"
    #input_image_folder_path = "C:/Users/Administrator.DESKTOP-BVT3B25/Desktop/密级截图样本1/"
    #output_path = "C:/Users/Administrator.DESKTOP-BVT3B25/Desktop/密级截图样本2/"
    #
    for root, dirs, files in os.walk(input_image_folder_path):
        for file in files:
            image_file_path = os.path.join(root, file)
            image_file_path = StringUtils.replaceBackSlash(image_file_path)
            convert_to_black_white_and_resize(image_file_path, output_path)

