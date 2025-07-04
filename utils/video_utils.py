#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.03.25 19:00
# @Author  : yida
# @File    : video_utils.py
# @Software: PyCharm
import os
import subprocess
import datetime
import cv2
import json


from utils.command_execute_utils import CommandExecuteUtils
from utils.file_utils import FileUtils
from utils.os_utils import OSUtils
from utils.string_utils import StringUtils

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

class VideoUtils:

    """
    获取视频文件的帧速率即fps
    """
    @staticmethod
    def get_fps_of(video_path: str):
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        return fps

    """
    获取视频文件的时间基即time_base
    """

    @staticmethod
    def get_time_base_of(video_path: str):
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=time_base',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        time_base_str = result.stdout.decode().strip().split('\n')[0]
        if time_base_str is None or len(time_base_str) <= 0 or "/" not in time_base_str:
            return 0
        try:
            time_base_str = time_base_str.split("/")[1].strip()
            return int(time_base_str)
        except Exception:
            return 0

    @staticmethod
    def put_timestamp_to_video(video_path: str, jpg_file_output_path: str, ffmpeg_path: str, fps:int):
        ffmpeg_path = StringUtils.replaceBackSlash(ffmpeg_path)
        video_path = StringUtils.replaceBackSlash(video_path)
        jpg_file_output_path = StringUtils.replaceBackSlash(jpg_file_output_path)
        jpg_file_output_path = StringUtils.to_ends_with_back_slash(jpg_file_output_path)
        video_filename = FileUtils.get_filename_without_suffix(video_path)
        jpg_file_parent_dir = jpg_file_output_path + video_filename
        if not os.path.exists(jpg_file_parent_dir):
            os.makedirs(jpg_file_parent_dir)

        script_params = (video_path, jpg_file_output_path, video_filename, ffmpeg_path, fps)
        if OSUtils.is_windows():
            script_path = project_basepath + "scripts/put_timestamp.bat"
        else:
            script_path = project_basepath + "scripts/put_timestamp.sh"
        result = True
        try:
            CommandExecuteUtils.execute_script(script_path, script_params)
        except Exception as e:
            # print(e)
            result = False
        finally:
            return result

    """
    从视频中抽取视频帧
    """
    @staticmethod
    def extract_frames_from_video(video_path: str, jpg_file_output_path: str, ffmpeg_path: str, fps:int,
                                  image_quality:int=2, image_width_height:str=None, enable_timestamp:bool=False):
        # image_quality参数: 1-31, 1表示图片质量最高, 31表示图片质量最低
        ffmpeg_path = StringUtils.replaceBackSlash(ffmpeg_path)
        ffmpeg_path = StringUtils.to_ends_with_back_slash(ffmpeg_path)
        video_path = StringUtils.replaceBackSlash(video_path)
        jpg_file_output_path = StringUtils.replaceBackSlash(jpg_file_output_path)
        jpg_file_output_path = StringUtils.to_ends_with_back_slash(jpg_file_output_path)
        video_filename = FileUtils.get_filename_without_suffix(video_path)
        jpg_file_parent_dir = jpg_file_output_path + video_filename
        if not os.path.exists(jpg_file_parent_dir):
            os.makedirs(jpg_file_parent_dir)
        if OSUtils.is_windows():
            ffmpeg_command_name = "ffmpeg.exe"
        else:
            ffmpeg_command_name = "ffmpeg"
        pts_text = "%{pts\:hms}"
        if enable_timestamp:
            if image_width_height is None or len(image_width_height) <= 0:
                command = (
                    f"{ffmpeg_path}bin/{ffmpeg_command_name} -i \"{video_path}\" -vf \"fps={fps},drawtext=text='{pts_text}':fontsize=30:fontcolor=white:box=1:boxcolor=black@0.5:x=10:y=10\" -q:v {image_quality} "
                    f"\"{jpg_file_output_path}{video_filename}/{video_filename}_%08d_%02d.jpg\"")
            else:
                command = (
                    f"{ffmpeg_path}bin/{ffmpeg_command_name} -i \"{video_path}\" -vf \"fps={fps},drawtext=text='{pts_text}':fontsize=30:fontcolor=white:box=1:boxcolor=black@0.5:x=10:y=10\" -q:v {image_quality} "
                    f"-s {image_width_height} \"{jpg_file_output_path}{video_filename}/{video_filename}_%08d_%02d.jpg\"")
        else:
            if image_width_height is None or len(image_width_height) <= 0:
                command = (f"{ffmpeg_path}bin/{ffmpeg_command_name} -i \"{video_path}\" -vf \"fps={fps}\" -q:v {image_quality} "
                           f"\"{jpg_file_output_path}{video_filename}/{video_filename}_%08d_%02d.jpg\"")
            else:
                command = (f"{ffmpeg_path}bin/{ffmpeg_command_name} -i \"{video_path}\" -vf \"fps={fps}\" -q:v {image_quality} "
                           f"-s {image_width_height} \"{jpg_file_output_path}{video_filename}/{video_filename}_%08d_%02d.jpg\"")
        result = True
        try:
            CommandExecuteUtils.execute_command(command)
        except Exception as e:
            print(e)
            result = False
        finally:
            return result

    @staticmethod
    def get_video_frame_count(video_file_path:str, ffmpeg_path:str):
        ffmpeg_path = StringUtils.replaceBackSlash(ffmpeg_path)
        ffmpeg_path = StringUtils.to_ends_with_back_slash(ffmpeg_path)
        if OSUtils.is_windows():
            ffprobe_path = f"{ffmpeg_path}bin/ffprobe.exe"
        else:
            ffprobe_path = f"{ffmpeg_path}bin/ffprobe"

        try:
            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-count_frames',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=nb_read_frames',
                '-of', 'json',
                video_file_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            data = json.loads(result.stdout)
            frames = int(data['streams'][0]['nb_read_frames'])
            return frames
        except:
            return 0


    @staticmethod
    def get_video_info(video_file_path:str, ffmpeg_path:str):
        ffmpeg_path = StringUtils.replaceBackSlash(ffmpeg_path)
        ffmpeg_path = StringUtils.to_ends_with_back_slash(ffmpeg_path)
        if OSUtils.is_windows():
            ffprobe_path = f"{ffmpeg_path}bin/ffprobe.exe"
        else:
            ffprobe_path = f"{ffmpeg_path}bin/ffprobe"
        cmd = [
            ffprobe_path,
             '-v', 'error',
            '-show_entries',
            'format=duration:stream=height,width,avg_frame_rate,nb_read_packets',
            '-of', 'json',
            video_file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.loads(result.stdout)

        # 解析数据
        stream = data['streams'][0]
        duration = int(float(data['format']['duration']))
        height = int(stream['height'])
        width = int(stream['width'])

        # 计算FPS
        fps_parts = stream['avg_frame_rate'].split('/')
        fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 0

        return {
            'duration': duration,
            'fps': fps,
            'width': width,
            'height': height
        }

    @staticmethod
    def get_video_duration(video_file_path: str):
        from videocr.opencv_adapter import Capture
        with Capture(video_file_path) as v:
            num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = v.get(cv2.CAP_PROP_FPS)

        # 计算视频时长（秒）
        if fps > 0:
            total_seconds = num_frames / fps

            # 将秒数转换为时间对象
            time_delta = datetime.timedelta(seconds=total_seconds)

            # 格式化为字符串
            if time_delta.total_seconds() < 3600:
                duration_str = str(time_delta).split('.')[0]
                if len(duration_str.split(':')) == 1:
                    duration_str = f"00:{duration_str.zfill(2)}"
                elif len(duration_str.split(':')) == 2:
                    mins, secs = duration_str.split(':')
                    duration_str = f"{mins.zfill(2)}:{secs.zfill(2)}"
                elif len(duration_str.split(':')) == 3:
                    hours, mins, secs = duration_str.split(':')
                    duration_str = f"{hours.zfill(2)}:{mins.zfill(2)}:{secs.zfill(2)}"
            else:
                # 手动格式化为 HH:MM:SS
                hours = int(time_delta.total_seconds() // 3600)
                minutes = int((time_delta.total_seconds() % 3600) // 60)
                seconds = int(time_delta.total_seconds() % 60)
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            # 如果无法获取FPS，返回默认值
            duration_str = "00:00"
        return duration_str


    @staticmethod
    def get_video_duration_str(video_duration:int):
        if video_duration <= 0:
            duration_str = "00:00"
        else:
            # 将秒数转换为时间对象
            time_delta = datetime.timedelta(seconds=video_duration)

            # 格式化为字符串
            if time_delta.total_seconds() < 3600:
                duration_str = str(time_delta).split('.')[0]
                if len(duration_str.split(':')) == 1:
                    duration_str = f"00:{duration_str.zfill(2)}"
                elif len(duration_str.split(':')) == 2:
                    mins, secs = duration_str.split(':')
                    duration_str = f"{mins.zfill(2)}:{secs.zfill(2)}"
                elif len(duration_str.split(':')) == 3:
                    hours, mins, secs = duration_str.split(':')
                    duration_str = f"{hours.zfill(2)}:{mins.zfill(2)}:{secs.zfill(2)}"
            else:
                # 手动格式化为 HH:MM:SS
                hours = int(time_delta.total_seconds() // 3600)
                minutes = int((time_delta.total_seconds() % 3600) // 60)
                seconds = int(time_delta.total_seconds() % 60)
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return duration_str



