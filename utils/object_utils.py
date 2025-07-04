#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.27 11:16
# @Author  : yida
# @File    : object_utils.py
# @Software: PyCharm

class ObjectUtils:
    @staticmethod
    def is_tuple(obj):
        if obj is None:
            return False
        return isinstance(obj, tuple)

    @staticmethod
    def is_dict(obj):
        if obj is None:
            return False
        return isinstance(obj, dict)

    @staticmethod
    def is_list(obj):
        if obj is None:
            return False
        return isinstance(obj, list)

    @staticmethod
    def is_str(obj):
        if obj is None:
            return False
        return isinstance(obj, str)

    @staticmethod
    def is_int(obj):
        if obj is None:
            return False
        return isinstance(obj, int)

    @staticmethod
    def is_float(obj):
        if obj is None:
            return False
        return isinstance(obj, float)

    @staticmethod
    def is_bool(obj):
        if obj is None:
            return False
        return isinstance(obj, bool)

    """
    将一个tuple映射成一个dict
    """

    @staticmethod
    def tuple_2_dict(tuple_obj: tuple, key_mappings: dict):
        target_dict = {}
        for index, val in enumerate(tuple_obj):
            if not index in key_mappings.keys():
                continue
            key = key_mappings[index]
            target_dict[key] = val
        return target_dict


    @staticmethod
    def group_by_four(lst):
        return [lst[i:i + 4] for i in range(0, len(lst), 4)]
