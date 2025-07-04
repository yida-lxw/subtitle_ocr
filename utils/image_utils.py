# -*- coding: UTF-8 -*-
from importlib.util import source_hash
from pydoc import source_synopsis

import cv2
import os
from PIL import Image

from utils.date_utils import DateUtils
from utils.file_utils import FileUtils
from utils.string_utils import StringUtils


class ImageUtils:
    @staticmethod
    def get_image_size(image_file_path):
        try:
            with Image.open(image_file_path) as img:
                width, height = img.size
                return width, height
        except Exception as e:
            print(f"Error: {e}")
            return None

    """
    将tif文件转换为常规的图片文件(如jpg或png)
    flags: 0表示单通道灰度图， -1表示读取所有通道数据， 1表示仅读取BGR通道数据
    """

    @staticmethod
    def tif_to_image(image_input_path, image_output_path, image_format="JPEG", flags: int = -1):
        image = cv2.imread(image_input_path, flags=flags)
        cv2.imwrite(image_output_path, image)
        pil_image = Image.open(image_output_path)
        pil_image.convert("RGB").save(image_output_path, format=image_format)

    @staticmethod
    def convert_png_to_jpg(png_image_path, jpg_image_path):
        try:
            with Image.open(png_image_path) as image:
                image.convert('RGB').save(jpg_image_path, 'JPEG', quality=100)
            return True, jpg_image_path
        except:
            return False, png_image_path


    #根据检测框bbox裁剪图片
    @staticmethod
    def crop_bbox_images(source_image_file_path, bbox, image_save_dir:str):
        if not os.path.exists(image_save_dir):
            os.makedirs(image_save_dir)
        image_save_dir = StringUtils.replaceBackSlash(image_save_dir)
        image_save_dir = StringUtils.to_ends_with_back_slash(image_save_dir)

        source_image_file_path = StringUtils.replaceBackSlash(source_image_file_path)
        source_image_filename = FileUtils.get_filename_without_suffix(source_image_file_path)
        source_image = cv2.imread(source_image_file_path)

        # x:检测框相对原图左上角(0,0)位置的x坐标
        # y:检测框相对原图左上角(0,0)位置的y坐标
        # w:检测框的宽度
        # h:检测框的高度
        x, y, w, h = map(int, bbox)

        # 执行裁剪
        crop_img = source_image[y:y+h, x:x+w]
        current_time = DateUtils.get_current_time_formatted()
        save_image_file_path = os.path.join(image_save_dir, f"{source_image_filename}_croped_{current_time}.jpg")
        try:
            cv2.imwrite(save_image_file_path, crop_img)
            return True, save_image_file_path
        except:
            return False, source_image_file_path



    # 判断检测框是否有效
    @staticmethod
    def is_valid_bbox(img_width, img_height, x, y, w, h, tolerance=0.5):
        """
        判断检测框是否有效（基于中线双轴偏移校验）
        :param img_width: 原始图片宽度
        :param img_height: 原始图片高度
        :param x: 检测框中心点x坐标
        :param y: 检测框中心点y坐标
        :param w: 检测框宽度
        :param h: 检测框高度
        :param tolerance: 中线允许误差（默认20像素）
        :return: True有效 / False无效
        """
        # 计算原始图片中线坐标
        img_center_x = img_width / 2
        img_center_y = img_height / 2

        # 计算检测框的中线坐标
        bbox_center_x = x + w / 2
        bbox_center_y = y + h / 2

        # 计算双轴偏移量（绝对值）
        horizontal_offset = abs(bbox_center_x - img_center_x)
        vertical_offset = abs(bbox_center_y - img_center_y)

        radio_x = horizontal_offset / img_width
        radio_y = vertical_offset / img_height
        # 有效性判断：水平或垂直任一方向偏移超过阈值即为无效
        return radio_x <= tolerance and radio_y <= tolerance

    # 在图片上绘制检测框
    @staticmethod
    def draw_box_on_image(source_image_file_path, bbox, image_save_path:str, color=(0, 255, 0)):
        image = cv2.imread(source_image_file_path)

        x_center = bbox[0]
        y_center = bbox[1]
        w = bbox[2]
        h = bbox[3]
        x = x_center - w / 2
        y = y_center - h / 2
        x_end = x_center + w / 2
        y_end = y_center + h / 2

        thickness = 2

        # 绘制矩形
        cv2.rectangle(image, (int(x), int(y)), (int(x_end), int(y_end)), color, thickness)
        cv2.imwrite(image_save_path, image)



