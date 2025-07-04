#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.03 11:46
# @Author  : yida
# @File    : test_sequence_to_timestamp.py
# @Software: PyCharm
import os
from pathlib import Path

from extract_timestamp import determin_timestamp_by_file_name


if __name__ == '__main__':
    file_name = "功夫_ass_00000438_438"
    (hour, min, second, million_second) = determin_timestamp_by_file_name(file_name)
    print(f"{hour}:{min}:{second}.{million_second}")






