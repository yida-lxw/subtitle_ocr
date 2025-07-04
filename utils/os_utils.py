# -*- coding: utf-8 -*-

import sys

class OSUtils:
    @staticmethod
    def get_os_type():
        if sys.platform.startswith('linux'):
            system_type = 'linux'
        elif sys.platform.startswith('win'):
            system_type = 'windows'
        elif sys.platform.startswith('darwin') or sys.platform.startswith('mac'):
            system_type = 'macOS'
        else:
            system_type = "unknown"
        return system_type

    @staticmethod
    def is_windows():
        os_type = OSUtils.get_os_type()
        return "windows" == os_type

    @staticmethod
    def is_linux():
        os_type = OSUtils.get_os_type()
        return "linux" == os_type

    @staticmethod
    def is_macos():
        os_type = OSUtils.get_os_type()
        return "macOS" == os_type