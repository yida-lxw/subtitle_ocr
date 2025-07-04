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

