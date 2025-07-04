# -*- coding: UTF-8 -*-
import os
from utils.file_utils import FileUtils

"""
已标注图片数据集最终检查：
主要检查图片个数与标签个数是否一致
"""


def check_label_more_than_image(image_dir, label_dir, require_delete=False):
    """检查标签文件是否多于图片文件，并处理多余标签"""
    image_files = FileUtils.get_file_list(image_dir)
    if not image_files:
        print("no image file.")
        return

    label_files = FileUtils.get_file_list(label_dir)
    if not label_files:
        print("no label file.")
        return

    # 提取图片文件名（不含扩展名）
    image_basenames = set()
    for img_path in image_files:
        filename = os.path.basename(img_path)
        basename = os.path.splitext(filename)[0]
        image_basenames.add(basename)

    # 检查标签文件
    for lbl_path in label_files:
        filename = os.path.basename(lbl_path)
        basename = os.path.splitext(filename)[0]

        if basename not in image_basenames:
            print(f"找不到对应图片的标签文件: {filename}")
            if require_delete:
                try:
                    os.remove(lbl_path)
                    print(f"标签文件: {filename} 删除成功")
                except Exception as e:
                    print(f"标签文件: {filename} 删除失败，错误：{e}")


def check_image_more_than_label(image_dir, label_dir, require_delete=False):
    """检查图片文件是否多于标签文件，并处理多余图片"""
    image_files = FileUtils.get_file_list(image_dir)
    if not image_files:
        print("no image file.")
        return

    label_files = FileUtils.get_file_list(label_dir)
    if not label_files:
        print("no label file.")
        return

    # 提取标签文件名（不含扩展名）
    label_basenames = set()
    for lbl_path in label_files:
        filename = os.path.basename(lbl_path)
        basename = os.path.splitext(filename)[0]
        label_basenames.add(basename)

    # 检查图片文件
    for img_path in image_files:
        filename = os.path.basename(img_path)
        basename = os.path.splitext(filename)[0]

        if basename not in label_basenames:
            print(f"找不到标签对应的图片文件: {filename}")
            if require_delete:
                try:
                    os.remove(img_path)
                    print(f"图片文件: {filename} 删除成功")
                except Exception as e:
                    print(f"图片文件: {filename} 删除失败，错误：{e}")


if __name__ == "__main__":
    base_dir = "D:/tmp/已标注/voc/"
    category_type = "subtitle"

    image_file_path = os.path.join(base_dir, category_type, "images")
    label_file_path = os.path.join(base_dir, category_type, "labels")

    check_label_more_than_image(image_file_path, label_file_path, require_delete=True)
    check_image_more_than_label(image_file_path, label_file_path, require_delete=True)
