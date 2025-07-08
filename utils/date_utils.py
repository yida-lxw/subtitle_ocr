# -*- coding: utf-8 -*-

from datetime import datetime

"""
日期操作工具类
"""


class DateUtils:
    """
    获取当前时间的字符串，以yyyyMMddhhmmss格式返回
    """

    @staticmethod
    def get_current_time_formatted(formate: str = "%Y%m%d%H%M%S") -> str:
        now = datetime.now()
        return now.strftime(formate)

    @staticmethod
    def larger_than(time1:str, time2:str):
        time_arr1 = time1.split(":")
        time_arr2 = time2.split(":")
        if len(time_arr1) == 1 and len(time_arr2) == 1:
            return int(time_arr1[0]) > int(time_arr2[0])
        if len(time_arr1) == 1 and len(time_arr2) == 2:
            minitue2 = time_arr2[1]
            return int(time_arr1[0]) > int(time_arr2[0])


