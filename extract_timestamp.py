#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.03 11:46
# @Author  : yida
# @File    : extract_timestamp.py
# @Software: PyCharm

def determin_sequence_no(file_name: str):
    parts = file_name.split('_')
    second_last = parts[-2]
    return int(second_last)


def get_quotient_remainder(n: int) -> tuple:
    quotient = n // 60
    remainder = n % 60
    return (quotient, remainder)

# 判断是否为偶数
def is_even_num(num: int) -> tuple:
    return num % 2 == 0

def determin_timestamp_by_sequnce_num(sequnce_num: int):
    temp_num = sequnce_num // 2
    quotient, remainder = get_quotient_remainder(temp_num)
    if quotient >= 60:
        hour = quotient // 60
        min = quotient % 60
    else:
        hour = 0
        min = quotient
    if is_even_num(sequnce_num):
        second = remainder - 1
        million_second = 500
    else:
        second = remainder
        million_second = 0
    return (hour, min, second, million_second)


def determin_timestamp_by_file_name(file_name: str):
    sequnce_num = determin_sequence_no(file_name)
    return determin_timestamp_by_sequnce_num(sequnce_num)