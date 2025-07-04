#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.16 18:09
# @Author  : yida
# @File    : test_get_file_hash.py
# @Software: PyCharm
from utils.file_utils import FileUtils

if __name__ == '__main__':
    file_path = r"E:/BadiduNetDiskDownload/test/测试文件001.mp4"

    file_hash = FileUtils.get_md5_of_file(file_path)
    print(file_hash)


