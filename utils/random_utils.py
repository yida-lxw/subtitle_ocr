# -*- coding: utf-8 -*-

import random

class RandomUtils:
    @staticmethod
    def random_float(min:float, max:float):
        random_number = random.uniform(min, max)
        return random_number

    @staticmethod
    def random_int(min:int, max:int):
        random_number = random.randint(min, max)
        return random_number