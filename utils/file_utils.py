# -*- coding: utf-8 -*-

import hashlib
import os
import shutil
from pathlib import Path
from tqdm import tqdm
from utils.string_utils import StringUtils

'''
@Project  easy-post 
@File     file_utils.py
@IDE      PyCharm
@Desc     文件操作工具类
'''


class FileUtils:
    @staticmethod
    def copy_file(src_file, dest_file):
        try:
            shutil.copyfile(src_file, dest_file)
            return True
        except:
            return False

    @staticmethod
    def get_files_in(directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    @staticmethod
    def get_file_list(dir_path):
        """获取目录下所有文件的路径列表"""
        if not os.path.isdir(dir_path):
            return []
        return [os.path.join(dir_path, f) for f in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, f))]

    @staticmethod
    # 删除指定文件
    def deleteFileIfExists(file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except:
                return False
        else:
            return False

    @staticmethod
    # 删除指定目录
    def deleteFolderIfExists(folder_path):
        if os.path.exists(folder_path):
            shutil.rmtree(path=folder_path, ignore_errors=True)

    """
    从给定文件路径中提取文件名(包含文件后缀名)
    """

    @staticmethod
    def get_filename_with_suffix(file_path):
        file_name = os.path.basename(file_path)
        return file_name


    """
    从给定文件路径中提取文件名(不包含文件后缀名)
    """
    @staticmethod
    def get_filename_without_suffix(file_path):
        file_name = os.path.basename(file_path)
        file_name = os.path.splitext(file_name)[0]
        return file_name

    """
    从给定文件名称中提取文件后缀名(不带点号)
    """
    @staticmethod
    def get_suffix(file_name: str, include_dot: bool = False):
        index = file_name.find(".")
        if index == -1:
            return ""
        if not include_dot:
            index = index + 1
        suffix = file_name[index: len(file_name)]
        return suffix

    """
    从文件名称中提取不包含后缀名的文件名
    """
    @staticmethod
    def get_file_name_without_suffix(file_name: str):
        index = file_name.find(".")
        if index == -1:
            return file_name
        target_file_name = file_name[0: index]
        return target_file_name

    """
    从文件名称中提取后缀名(带点号)
    """
    @staticmethod
    def get_file_suffix(file_name: str):
        index = file_name.find(".")
        if index == -1:
            return ""
        target_file_suffix = file_name[index: len(file_name)]
        return target_file_suffix

    # 复制目录及其所有子文件和子目录
    @staticmethod
    def copyFolder(source_folder_path, target_folder_path):
        shutil.copytree(source_folder_path, target_folder_path)

    # 文件重命名
    @staticmethod
    def rename_file(orignal_file_path, new_file_name):
        if StringUtils.is_empty(orignal_file_path) or StringUtils.is_empty(new_file_name):
            return False
        parent_dir = os.path.dirname(orignal_file_path)
        parent_dir = StringUtils.replaceBackSlash(parent_dir)
        parent_dir = StringUtils.to_ends_with_back_slash(parent_dir)
        file_name = os.path.basename(orignal_file_path)
        new_suffix = FileUtils.get_suffix(new_file_name, include_dot=True)
        if StringUtils.is_not_empty(new_suffix):
            new_suffix = new_suffix.lower()
            target_new_file_name = FileUtils.get_file_name_without_suffix(new_file_name)
            final_new_file_name = target_new_file_name + new_suffix
        else:
            final_new_file_name = new_file_name
        # 若新文件名与原始文件名相同,则不需要执行文件重命名操作
        if StringUtils.equals(file_name, final_new_file_name):
            return False
        new_file_abspath = os.path.join(parent_dir, final_new_file_name)
        try:
            os.rename(orignal_file_path, new_file_abspath)
            return True
        except Exception as e:
            return False

    # 往文本文件中写入字符串内容
    @staticmethod
    def write_string_to_file(content_to_write: str, file_path: str, encoding: str = "UTF-8"):
        write_result = True
        try:
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(content_to_write)
        except:
            write_result = False
        finally:
            return write_result

    # 读取指定文件并返回字符串
    @staticmethod
    def read_file_as_string(file_path: str, encoding: str = "UTF-8") -> str:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            return content

    # 读取指定文件并以list[str]形式返回文件中每一行的文本
    @staticmethod
    def read_file_as_lines(file_path: str, encoding: str = "UTF-8") -> list:
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()
            return lines

    """
    获取当前目录下的子文件，不包括目录， 且不包括子目录下的文件
    """

    @staticmethod
    def get_subfiles_in_folder(source_folder) -> list:
        dir_path = Path(source_folder)
        try:
            return [StringUtils.replaceBackSlash(str(file)) for file in dir_path.iterdir() if file.is_file()]
        except Exception as e:
            return []

    """
    获取当前目录下的子目录，不包括文件， 且不包括子目录下的子目录，只搜寻当前目录所在层级
    """

    @staticmethod
    def get_subfolderes_in_folder(source_folder) -> list:
        dir_path = Path(source_folder)
        try:
            return [StringUtils.replaceBackSlash(str(folder)) for folder in dir_path.iterdir() if
                    os.path.isdir(str(folder))]
        except Exception as e:
            return []

    """
    判断指定目录下是否只有文件没有子目录(空目录会返回False)
    """

    @staticmethod
    def has_only_files(source_folder) -> bool:
        try:
            dir_items = FileUtils.get_subfolderes_in_folder(source_folder)
            subfile_items = FileUtils.get_subfiles_in_folder(source_folder)
            if len(dir_items) <= 0 and len(subfile_items) > 0:
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件的体积大小（单位：bytes）

        Args:
            file_path (str): 文件路径

        Returns:
            int: 文件的字节大小
        """

        if not os.path.exists(file_path):
            return -1

        if not os.path.isfile(file_path):
            raise OSError(f"路径 '{file_path}' 不是文件")
        return os.path.getsize(file_path)

    @staticmethod
    def get_md5_of_file(file_path, block_size=4096):
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(block_size):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @staticmethod
    def safe_merge(input_dir, output_merge_file_path, chunk_suffix='.part', buffer_size=5 * 1024 * 1024):
        merge_result = False
        try:
            # 获取排序后的分片文件列表
            chunks = sorted([f for f in os.listdir(input_dir) if f.endswith(chunk_suffix)])

            # 合并文件
            with open(output_merge_file_path, 'wb') as outfile, tqdm(total=len(chunks), desc='文件分片合并进度') as pbar:
                for chunk in chunks:
                    chunk_path = os.path.join(input_dir, chunk)
                    with open(chunk_path, 'rb') as infile:
                        shutil.copyfileobj(infile, outfile, buffer_size)
                    pbar.update(1)
            print(f"文件合并完成,保存至{output_merge_file_path}")
            merge_result = True
        except Exception as e:
            print(f"合并失败: {str(e)}")
            FileUtils.deleteFileIfExists(output_merge_file_path)
        finally:
            return merge_result
