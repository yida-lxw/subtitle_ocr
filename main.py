#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025.04.15 14:55
# @Author  : yida
# @File    : main.py
# @Software: PyCharm
import asyncio
import hashlib
import json
import os
import shutil

import aiofiles
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile

from ass_to_srt import ass_to_srt
from config.app_config import APPConfig
from config.thread_pool_config import ThreadPoolConfig
from db_pool import SQLTemplate
from extract_soft_subtitle import extract_soft_subtitles
from hard_subtitle_extractor import HardSubtitleExtractor
from hard_subtitle_ocr_result_writer import HardSubtitleOcrResultWriter, HardSubtitleOcrResultInfo
from id_worker import IdWorker
from kv_ttl_cache import KVTTLCache
from sub_to_srt import sub_to_srt
from thread_pool.thread_pool_manager import ThreadPoolManager
from utils.file_utils import FileUtils
from utils.string_utils import StringUtils
from utils.subtitle_utils import SubtitleUtils
from utils.video_utils import VideoUtils
from video_subtitle_status_resume import VideoSubtitleStatusResume
from videocr.video import Video

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

id_worker = IdWorker(datacenter_id=1, worker_id=1, sequence=1)

# 加载配置文件
app_config_path = "config/app.yml"
thread_pool_config_path = "config/thread_pool.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)
thread_pool_config_loaded = ThreadPoolConfig.load_thread_pool_config(project_basepath, thread_pool_config_path)
# 初始化线程池管理器
thread_pool_manager = ThreadPoolManager(thread_pool_config=thread_pool_config_loaded)

work_dir: str = app_config_loaded.work_dir
upload_dir: str = app_config_loaded.upload_relative_dir
work_dir = StringUtils.replaceBackSlash(work_dir)
work_dir = StringUtils.to_ends_with_back_slash(work_dir)
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

# 接收文件的缓冲区大小，单位为字节, 默认为5M
RECEIVE_CHUNK_SIZE = 1024 * 1024 * 5

video_file_suffix = [
    "avi",
    "mp4",
    "mkv",
    "mov",
    "rmvb",
    "webm"
]

video_file_suffix_for_soft = [
    "mp4",
    "mkv",
    "mov",
    "avi"
]

table_name = app_config_loaded.video_hard_subtitle_ocr_table_name

# 初始化SQLLite表
sql_template = SQLTemplate()
hard_subtitle_ocr_result_writer = HardSubtitleOcrResultWriter(sql_template)
hard_subtitle_ocr_result_writer.create_table()

enable_subtitle_cache = app_config_loaded.enable_subtitle_cache
kv_cache = KVTTLCache()

video_subtitle_status_resume = VideoSubtitleStatusResume(app_config_loaded, sql_template, kv_cache)
video = Video(app_config_loaded)
hard_subtitle_extractor = HardSubtitleExtractor(video, app_config_loaded)
app = FastAPI()

task_registry = {}

async def run_in_threadpool(func, *args):
    """在专用线程池中运行同步函数"""
    loop = asyncio.get_running_loop()
    thread_pool = thread_pool_manager.get_thread_pool_executor()
    return await loop.run_in_executor(thread_pool, func, *args)

def handle_file_merge(upload_file_parent_path, target_file_path):
    FileUtils.safe_merge(upload_file_parent_path, target_file_path)

async def calculate_file_md5(upload_file: UploadFile) -> str:
    md5_hash = hashlib.md5()
    await upload_file.seek(0)
    while chunk := await upload_file.read(8192):
        md5_hash.update(chunk)
    await upload_file.seek(0)
    return md5_hash.hexdigest()

async def write_file_chunk(file: UploadFile, upload_file_parent_path: str, file_name: str, chunk_index: int):
    chunk_index_str = StringUtils.left_pad_zero(int(chunk_index), 8)
    chunk_file_path = os.path.join(upload_file_parent_path, f"{file_name}_{chunk_index_str}.part")
    async with aiofiles.open(chunk_file_path, "wb") as f:
        remaining = RECEIVE_CHUNK_SIZE
        while remaining > 0:
            chunk = await file.read(min(remaining, 1024 * 1024))
            if not chunk:
                break
            await f.write(chunk)
            remaining -= len(chunk)
        await f.flush()


def prepare_hard_subtitle_info_from_db(file_hash: str, time_start:str, time_end: str):
    subtitle_info = hard_subtitle_ocr_result_writer.load_hard_subtitle(file_hash, time_start, time_end)
    if subtitle_info is None:
        return None
    else:
        task_id = subtitle_info[1]
        file_hash = subtitle_info[2]
        srt_content = subtitle_info[3]
        srt_content_list = json.loads(srt_content)
        return {
            "code": 200,
            "message": "ok",
            "task_id": task_id,
            "file_hash": file_hash,
            "time_start": time_start,
            "time_end": time_end,
            "data": srt_content_list
        }



def handle_solf_subtitle(upload_video_file_path, original_video_filename, work_dir, subtitle_output_dir,
                         ffmpeg_basepath,
                         encoding: str = 'utf-8'):
    task_id = id_worker.get_id()
    subtitle_output_path = work_dir + task_id + "/" + subtitle_output_dir + "/"
    if not os.path.exists(subtitle_output_path):
        os.makedirs(subtitle_output_path)
    os.makedirs(subtitle_output_path, exist_ok=True)
    extract_result = extract_soft_subtitles(upload_video_file_path, ffmpeg_basepath,
                                            subtitle_output_dir=subtitle_output_path)
    print(
        f"视频文件{upload_video_file_path}的内嵌软字幕提取任务执行成功,字幕文件保存在{subtitle_output_path},任务ID为{task_id}.")
    if not extract_result:
        print(f"提取视频文件{upload_video_file_path}的内嵌软字幕失败,请稍后重试.")
        return {"code": 200, "message": "error", "data": [], "file_name": original_video_filename}
    subtitle_file_list = FileUtils.get_file_list(subtitle_output_path)
    if len(subtitle_file_list) <= 0:
        print(f"找不到从视频文件{upload_video_file_path}提取的内嵌软字幕文件,可能字幕提取过程中出现异常.")
        return {"code": 200, "message": "error", "data": [], "file_name": original_video_filename}
    target_subtitle_list = []
    for subtitle_file_path in subtitle_file_list:
        print(f"开始解析字幕文件:{subtitle_file_path}")
        subtitle_filename = FileUtils.get_filename_with_suffix(subtitle_file_path)
        subtitle_file_suffix = FileUtils.get_suffix(subtitle_filename).lower()
        if subtitle_file_suffix == "srt":
            file_content = FileUtils.read_file_as_string(subtitle_file_path, encoding=encoding)
            convert_result, target_subtitle_list = SubtitleUtils.parse_srt_subtitle(file_content)
            break
        elif subtitle_file_suffix == "ass":
            convert_result, target_subtitle_list = ass_to_srt(ass_file_path=subtitle_file_path, srt_file_path=None,
                                                              encoding=encoding)
            break
        elif subtitle_file_suffix == "sub":
            fps = VideoUtils.get_fps_of(upload_video_file_path)
            convert_result, target_subtitle_list = sub_to_srt(sub_file_path=subtitle_file_path, srt_file_path=None,
                                                              fps=fps, encoding=encoding)
            break
    status_code = 200
    message = "ok" if convert_result else "error"
    FileUtils.deleteFileIfExists(upload_video_file_path)
    return {"code": status_code, "message": message, "data": target_subtitle_list, "file_name": original_video_filename}


@app.post("/slice_upload")
async def slice_upload_file(
        file: UploadFile = File(...)
):
    work_dir: str = app_config_loaded.work_dir
    upload_dir: str = app_config_loaded.upload_relative_dir
    work_dir = StringUtils.replaceBackSlash(work_dir)
    work_dir = StringUtils.to_ends_with_back_slash(work_dir)
    file_name = file.filename
    file_name_without_suffix = FileUtils.get_file_name_without_suffix(file_name)
    file_type = FileUtils.get_suffix(file_name, include_dot=False)
    file_hash = await calculate_file_md5(file)
    upload_file_parent_path = work_dir + upload_dir + "/" + file_name_without_suffix + "/" + file_type + "/chunks/" + file_hash + "/"
    if not os.path.exists(upload_file_parent_path):
        os.makedirs(upload_file_parent_path)
    file_size = file.size
    if file_size % RECEIVE_CHUNK_SIZE == 0:
        chunk_count = int(file_size / RECEIVE_CHUNK_SIZE)
    else:
        chunk_count = int(file_size / RECEIVE_CHUNK_SIZE) + 1

    # await asyncio.gather(*[
    #     write_file_chunk(file, upload_file_parent_path, file_name_without_suffix, chunk_index)
    #     for chunk_index in range(1, chunk_count + 1)
    # ])
    for chunk_index in range(1, chunk_count + 1):
        await write_file_chunk(file, upload_file_parent_path, file_name_without_suffix, chunk_index)

    return {
        "file_hash": file_hash,
        "chunk_count": chunk_count,
        "file_name": file_name_without_suffix,
        "file_type": file_type,
        "file_size": file_size,
        "status": "file_received"
    }


@app.post("/file_merge")
async def upload_file_merge(
        file_hash: str = Form(...),
        chunk_count: str = Form(...),
        file_name: str = Form(...),
        file_type: str = Form(...),
        file_size: str = Form(...)
):
    upload_file_parent_path = work_dir + upload_dir + "/" + file_name + "/" + file_type + "/chunks/" + file_hash + "/"
    if not os.path.exists(upload_file_parent_path):
        return {"code": 200, "message": "upload folder not exists", "data": [],
                "file_name": file_name, "file_type": file_type, "file_size": file_size, "file_hash": file_hash}

    part_file_list = [os.path.join(upload_file_parent_path, f) for f in os.listdir(upload_file_parent_path)
                      if os.path.isfile(os.path.join(upload_file_parent_path, f)) and f.endswith(".part")]
    part_file_count = len(part_file_list)
    if part_file_count != int(chunk_count):
        return {"code": 200, "message": "part file count not equals to chunk_count", "data": [],
                "file_name": file_name, "file_type": file_type, "file_size": file_size, "file_hash": file_hash}

    target_filename = file_name + "." + file_type
    target_file_path = upload_file_parent_path + target_filename
    if not os.path.exists(target_file_path):
        #asyncio.create_task(handle_file_merge(upload_file_parent_path, target_file_path))
        task = asyncio.create_task(
            run_in_threadpool(handle_file_merge, upload_file_parent_path, target_file_path)
        )

        # 将任务添加到注册表（防止垃圾回收）
        task_registry[file_hash] = task

        # 添加完成回调（自动清理注册表）
        task.add_done_callback(lambda t: task_registry.pop(file_hash, None))

        return {"code": 200, "message": "ok", "status": "file_merging", "data": [],
                "file_name": file_name, "file_type": file_type, "file_size": file_size,
                "file_hash": file_hash}
    else:
        actual_file_size = FileUtils.get_file_size(target_file_path)
        if str(actual_file_size) == file_size:
            return {"code": 200, "message": "ok", "status": "ready_for_subtitle_extraction", "data": [],
                    "file_name": file_name, "file_type": file_type, "file_size": file_size, "file_hash": file_hash}
        return {"code": 200, "message": "ok", "status": "file_merging", "data": [],
                    "file_name": file_name, "file_type": file_type, "file_size": file_size, "file_hash": file_hash}

"""
根据文件摘要提取硬字幕数据
"""
@app.post("/hard_subtitle_extract")
async def hard_subtitle_check_in(
        file_hash: str = Form(...),
        file_name: str = Form(...),
        file_type: str = Form(...),
        time_start: str = Form(default= "00:00"),
        time_end: str = Form(default= None),
        user_fullframe: bool= Form(default= False)):


    upload_file_parent_path = work_dir + upload_dir + "/" + file_name + "/" + file_type + "/chunks/" + file_hash + "/"
    target_filename = file_name + "." + file_type
    video_file_path = upload_file_parent_path + target_filename
    if not os.path.exists(video_file_path):
        return {
            "code": 200,
            "message": "ok",
            "status": "target video file not found",
            "data": []
        }

    if StringUtils.is_empty(time_end):
        video_duration = VideoUtils.get_video_duration(video_file_path)
        time_end = video_duration
    cache_key = file_hash + "#" + time_start + "#" + time_end
    if enable_subtitle_cache:
        response_json = kv_cache.get(cache_key)
        if response_json is not None and len(response_json) > 0:
            return response_json
    if enable_subtitle_cache:
        subtitle_info = prepare_hard_subtitle_info_from_db(file_hash, time_start, time_end)
        if subtitle_info is not None:
            return subtitle_info

    hard_subtitle_extractor.set_user_fullframe(user_fullframe)
    subtitle_content = hard_subtitle_extractor.extract_hard_subtitle(video_file_path, time_start, time_end)
    if StringUtils.is_empty(subtitle_content):
        return {
            "code": 200,
            "message": "ok",
            "status": "no hard subtitle extracted",
            "data": []
        }
    parse_result, hard_subtitle_list = hard_subtitle_extractor.parse_subtitle_as_list(subtitle_content)
    if not parse_result:
        return {
            "code": 200,
            "message": "ok",
            "status": "parse subtitle failed",
            "data": []
        }

    task_id = id_worker.get_id()
    response_data = {
        "code": 200,
        "message": "ok",
        "status": "success",
        "task_id": task_id,
        "file_hash": file_hash,
        "time_start": time_start,
        "time_end": time_end,
        "data": hard_subtitle_list
    }
    if hard_subtitle_list is not None and len(hard_subtitle_list) > 0:
        kv_cache.set(cache_key, response_data)
        subtitle_content_json = StringUtils.to_json_str(hard_subtitle_list)
        hard_subtitle_ocr_result_info = HardSubtitleOcrResultInfo(task_id, file_hash, time_start, time_end, subtitle_content_json)
        hard_subtitle_ocr_result_writer.save_ocr_result(hard_subtitle_ocr_result_info)
    return response_data


# 视频硬字幕提取过程中产生的缓存数据清理
@app.post("/clean_hard_subtitle_cache")
async def clean_subtitle_cache(file_hash: str = Form(...), from_scratch: bool = Form(default=False)):
    try:
        video_subtitle_status_resume.clean_cache(file_hash)
        if from_scratch:
            video_subtitle_status_resume.resume(file_hash)
        return {"code": 200, "message": "ok"}
    except Exception:
        return {"code": 500, "message": "error"}


"""
提取视频文件的内嵌软字幕(基于FFMpeg工具)
"""
@app.post("/soft_subtitle_extract")
async def soft_subtitle_extract(file: UploadFile = File(...), ffmpeg_basepath: str = app_config_loaded.ffmpeg_path,
                                subtitle_output_dir: str = app_config_loaded.extracted_soft_subtitles_dir,
                                encoding: str = 'utf-8'):
    original_video_filename = file.filename
    file_suffix = FileUtils.get_suffix(original_video_filename)
    if file_suffix not in video_file_suffix_for_soft:
        return {
            "code": 200,
            "message": f"不支持的文件类型 {file_suffix}，请上传视频文件（MP4/MOV/MKV/AVI）"
        }
    work_dir = app_config_loaded.work_dir
    work_dir = StringUtils.replaceBackSlash(work_dir)
    work_dir = StringUtils.to_ends_with_back_slash(work_dir)
    upload_dir_path = work_dir + app_config_loaded.upload_relative_dir + "/"
    if not os.path.exists(upload_dir_path):
        os.makedirs(upload_dir_path)
    upload_video_file_path = upload_dir_path + original_video_filename
    try:
        with open(upload_video_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"视频文件上传成功,已保存至{upload_video_file_path}.")
    except:
        print(f"上传文件{original_video_filename}失败，请重新上传.")
        return {"code": 500, "message": f"上传文件{original_video_filename}失败，请重新上传."}

    return handle_solf_subtitle(upload_video_file_path, original_video_filename, work_dir, subtitle_output_dir,
                                ffmpeg_basepath, encoding)


if __name__ == '__main__':
    host = app_config_loaded.host
    if host is None or len(host) <= 0:
        host = StringUtils.get_local_ip()
    uvicorn.run(app='main:app', host=host, port=app_config_loaded.port,
                workers=app_config_loaded.workers)

