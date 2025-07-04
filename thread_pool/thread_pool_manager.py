#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.27 10:04
# @Author  : yida
# @File    : thread_pool_manager.py
# @Software: PyCharm
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from config.thread_pool_config import ThreadPoolConfig
from utils.object_utils import ObjectUtils

"""
线程池管理器
"""


class ThreadPoolManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, thread_pool_config: ThreadPoolConfig, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.thread_pool_executor = ThreadPoolExecutor(
                        max_workers=thread_pool_config.max_pool_size,
                        thread_name_prefix=thread_pool_config.thread_name_prefix
                    )
        return cls._instance

    def get_thread_pool_executor(self):
        return self.thread_pool_executor

    """
    往线程池提交任务
    """

    def submit_task(self, func, func_params, is_async_call: bool = False):
        executor = self.get_thread_pool_executor()
        if ObjectUtils.is_dict(func_params):
            future = executor.submit(func, **func_params)
        else:
            future = executor.submit(func, func_params)

        # 若需要异步调用，则返回future对象
        if is_async_call:
            return future
        func_return_result = future.result()
        return func_return_result

    """
        往线程池批量提交多个任务
    """

    def submit_multiple_task(self, func, func_params: dict, data_list: list, is_async_call: bool = False,
                             result_list_in_order: bool = False):
        if data_list is None or len(data_list) <= 0:
            return None
        executor = self.get_thread_pool_executor()

        future_list = [executor.submit(func, cur_list, **func_params) for cur_list in data_list]
        # 若需要异步调用，则返回future对象列表
        if is_async_call:
            return future_list

        # 是否需要按任务提交顺序来返回结果
        if result_list_in_order:
            # 按提交顺序返回结果（阻塞直到所有任务完成）
            return [future.result() for future in future_list]

        # 按完成顺序收集结果
        return [future.result() for future in as_completed(future_list)]

    def get_return_result_list(self, future_list: list, result_list_in_order: bool = False):
        if result_list_in_order:
            # 按提交顺序返回结果（阻塞直到所有任务完成）
            return [future.result() for future in future_list]

        # 按完成顺序收集结果
        try:
            result_list = []
            for future in as_completed(future_list):
                current_result = future.result()
                if current_result is None:
                    continue
                result_list.append(current_result)
            return result_list
        except Exception as e:
            return None
