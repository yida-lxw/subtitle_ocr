# -*- coding: utf-8 -*-

import json
import os
import random
import re
import socket
from opencc import OpenCC
from complex_encoder import ComplexEncoder
from utils.os_utils import OSUtils

'''
@Project  easy-post 
@File     string_utils.py
@IDE      PyCharm
@Desc     字符串操作工具类
'''
class StringUtils:
    """
    判断给定字符串是否为空
    """

    @staticmethod
    def is_empty(orignal_str: str):
        return orignal_str is None or len(orignal_str) == 0

    """
    判断给定字符串是否不为空
    """

    @staticmethod
    def is_not_empty(orignal_str: str):
        return not StringUtils.is_empty(orignal_str)

    # 查找指定字符在original_string字符串中最后一次出现的位置
    @staticmethod
    def lastIndexOf(original_string: str, substr: str) -> int:
        if original_string is None or substr is None:
            raise ValueError("string and substr could not be None.")
        elif not (isinstance(original_string, str) and isinstance(substr, str)):
            raise TypeError("string and substr must be str type.")
        elif not (len(original_string) > 0 and 0 < len(substr) <= len(original_string)):
            raise TypeError("string and substr value must be non empty, "
                            "and string's length must more over than substr's length.")
        last_index = -1
        idx = 0
        while True:
            try:
                index = original_string.index(substr, idx)
                last_index = index
                idx = index + len(substr)
            except ValueError:
                return last_index

    """
    判断两个字符串是否相等(比较时区分大小写)
    """
    @staticmethod
    def equals(str1: str, str2: str):
        if str1 is None and str2 is None:
            return True
        if str1 == "" and str2 == "":
            return True
        if str1 is None and str2 is not None:
            return False
        if str1 is not None and str2 is None:
            return False
        return str1 == str2

    """
    判断两个字符串是否不相等(比较时区分大小写)
    """

    @staticmethod
    def not_equals(str1: str, str2: str):
        return not StringUtils.equals(str1, str2)

    """
    判断两个字符串是否相等(比较时忽略字符串的大小写)
    """

    @staticmethod
    def equals_ignore_case(str1: str, str2: str):
        if str1 is None and str2 is None:
            return True
        if str1 == "" and str2 == "":
            return True
        if str1 is None and str2 is not None:
            return False
        if str1 is not None and str2 is None:
            return False
        return str1.lower() == str2.lower()

    """
    判断两个字符串是否不相等(比较时忽略字符串的大小写)
    """

    @staticmethod
    def not_equals_ignore_case(str1: str, str2: str):
        return not StringUtils.equals_ignore_case(str1, str2)

    """
    文件路径中的反斜杠\转换为正斜杠/
    """

    @staticmethod
    def replaceBackSlash(file_path: str):
        if StringUtils.is_empty(file_path):
            return file_path
        file_path = file_path.replace("\\", "/")
        return file_path

    """
    若文件路径不是以正斜杠/结尾, 则转化为以正斜杠/结尾
    """

    @staticmethod
    def to_ends_with_back_slash(file_path: str):
        if "\\" in file_path:
            file_path = StringUtils.replaceBackSlash(file_path)
        if file_path.endswith("/"):
            return file_path
        file_path = file_path + "/"
        return file_path

    """
    剔除掉末尾的正斜杠或反斜杠
    """

    @staticmethod
    def trim_last_slash(file_path: str):
        if "\\" in file_path:
            file_path = StringUtils.replaceBackSlash(file_path)
        if not file_path.endswith("/"):
            return file_path
        file_path = file_path[0: len(file_path) - 1]
        return file_path

    """
    数字添加前导字符,使其最终长度达到指定的total_len大小
    """
    @staticmethod
    def left_pad_zero(num: int, total_len: int = 5):
        return str(num).zfill(total_len)

    # 获取当前项目的根路径
    @staticmethod
    def get_project_basepath():
        # current_dir = os.getcwd()
        # while not os.path.exists(os.path.join(current_dir, 'requirements.txt')):
        #     current_dir = os.path.dirname(current_dir)
        # return current_dir
        current_dir = os.getcwd()
        min_depth = 0
        project_basepath = ''
        while current_dir:
            if current_dir == '/':
                break
            if len(current_dir) == 3 and current_dir[0].isupper() and current_dir[1] == ':' and current_dir[2] == '\\':
                break
            if os.path.exists(os.path.join(current_dir, 'requirements.txt')):
                depth = len(current_dir.split(os.sep)) - 1
                if depth < min_depth or min_depth == 0:
                    min_depth = depth
                    project_basepath = current_dir

            current_dir = os.path.dirname(current_dir)
        if project_basepath is not None and len(project_basepath) > 0:
            project_basepath = StringUtils.replaceBackSlash(project_basepath)
            project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)
        return project_basepath

    # 生成[start, end]区间内的随机数(双闭区间)
    @staticmethod
    def random_num(start, end):
        return random.randint(start, end)

    # 将Python对象格式化为JSON字符串
    @staticmethod
    def to_json_str(obj, beautify: bool = True, encoder=ComplexEncoder):
        if beautify:
            return json.dumps(obj, indent=4, ensure_ascii=False, cls=encoder)
        else:
            return json.dumps(obj, ensure_ascii=False, cls=encoder)

    # JSON字符串转成dict类型
    @staticmethod
    def json_to_dict(json_string: str) -> dict:
        dict_data = json.loads(json_string)
        return dict_data

    # 删除py文件中的注释
    @staticmethod
    def remove_comments(file_content):
        # First, find and store string assignments
        protected_strings = {}
        counter = 0

        def protect_string_assignments(match):
            nonlocal counter
            var_name, string_content = match.groups()
            key = f'PROTECTED_STRING_{counter}'
            protected_strings[key] = match.group(0)
            counter += 1
            return key

        # Protect strings that are part of assignments
        protected_content = re.sub(
            r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*)("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
            protect_string_assignments,
            file_content
        )

        # Remove docstring comments (triple-quoted strings not part of assignments)
        cleaned_content = re.sub(
            r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
            '',
            protected_content
        )

        # Remove single-line comments and empty lines
        lines = []
        for line in cleaned_content.split('\n'):
            # Remove inline comments
            line = re.sub(r'#.*$', '', line)
            if line.strip():
                lines.append(line)

        # Restore protected strings
        final_content = '\n'.join(lines)
        for key, value in protected_strings.items():
            final_content = final_content.replace(key, value)
        return final_content

    """
    判断给定文本中是否包含繁体字
    """

    @staticmethod
    def has_traditional_by_unicode(text):
        if text is None or len(text) <= 0:
            return False
        converter = OpenCC('t2s')
        return text != converter.convert(text)


    """
    繁体转简体
    """

    @staticmethod
    def to_simplified_chinese(text):
        if text is None or len(text) <= 0:
            return text
        converter = OpenCC('t2s')
        try:
            convert_result = converter.convert(text)
        except:
            convert_result = text
        finally:
            return convert_result


    # 判断给定的文本是否为IP地址或域名
    @staticmethod
    def is_ip_or_domain(text):
        if text is None or len(text) <= 0:
            return False
        # 判断是否为IPv4地址
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ipv4_pattern, text):
            return True

        # 判断是否为域名
        domain_pattern = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*\.[A-Za-z]{2,}$'
        if re.match(domain_pattern, text) and len(text) <= 253:
            return True

        return False


    # 判断给定的文件路径是否为绝对路径
    @staticmethod
    def is_absolute_path(path):
        if path is None or len(path) <= 0:
            return False

        if path.startswith("./") or path.startswith(".\\") or path.startswith("../") or path.startswith("..\\"):
            return False

        # 检查Linux/Mac的绝对路径
        if path.startswith('/') and (OSUtils.is_linux() or OSUtils.is_macos()):
            return True
        # 检查Windows盘符绝对路径（如C:\或C:/）
        if OSUtils.is_windows():
            path = StringUtils.replaceBackSlash(path)
            if len(path) >=11:
                if (path.startswith("file:///") or path.startswith("file:\\\\\\")):
                    if path[8].lower() in 'abcdefghijklmnopqrstuvwxyz' and path[9] == ':' and path[10] in ('/', '\\'):
                        return True
                    else:
                        temp_path = path.replace("file:///", "")
                        temp_path_array = temp_path.split("/")
                        ip = temp_path_array[0]
                        if ":" in ip:
                            ip_array = ip.split(":")
                            ip = ip_array[0]
                            port_str = ip_array[1]
                            try:
                                port = int(port_str)
                            except:
                                return False
                        if StringUtils.is_ip_or_domain(ip):
                            return True

                else:
                    if path[0].lower() in 'abcdefghijklmnopqrstuvwxyz' and path[1] == ':' and path[2] in ('/', '\\'):
                        return True
            elif len(path) >= 3 and path[0].lower() in 'abcdefghijklmnopqrstuvwxyz' and path[1] == ':' and path[2] in ('/', '\\'):
                return True
            # 检查Windows UNC路径（如\\server或//server）
            elif len(path) >= 2 and (path.startswith('\\\\') or path.startswith('//')):
                return True
        return False


    @staticmethod
    def is_punctuation(char):
        # 判断字符是否为中英文标点
        return char in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~，。！？；：“”‘’【】（）…—–·'


    # 获取本机局域网IP
    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip


    @staticmethod
    # 判断字符串是否全部由字母和数字组成
    def is_alphanumeric(text_str):
        return bool(re.fullmatch(r'^[a-zA-Z0-9]+$', text_str))



if __name__ == '__main__':
    # 测试示例
    print(StringUtils.is_alphanumeric("Hello123"))  # True
    print(StringUtils.is_alphanumeric("12345"))  # True
    print(StringUtils.is_alphanumeric("Python3"))  # True
    print(StringUtils.is_alphanumeric("Hello World"))  # False（包含空格）
    print(StringUtils.is_alphanumeric("Python@3"))  # False（包含特殊字符@）
    print(StringUtils.is_alphanumeric("你好"))  # False（包含中文字符）
    print(StringUtils.is_alphanumeric(""))  # False（空字符串）
