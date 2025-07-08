import os.path

from config.app_config import APPConfig
from utils.file_utils import FileUtils
from utils.string_utils import StringUtils
from utils.subtitle_utils import SubtitleUtils
from utils.video_utils import VideoUtils
from videocr import get_subtitles, save_subtitles_to_file
from videocr.video import Video

# 硬字幕提取器
class HardSubtitleExtractor:
    def __init__(self, video: Video, app_config: APPConfig):
        self.video = video
        self.app_config = app_config
        self.enable_output_hard_subtitle_file = self.app_config.enable_output_hard_subtitle_file
        work_dir = app_config.work_dir
        work_dir = StringUtils.replaceBackSlash(work_dir)
        work_dir = StringUtils.to_ends_with_back_slash(work_dir)
        self.srt_file_output_path = work_dir + app_config.hard_subtitle_output_folder + "/"
        if not os.path.exists(self.srt_file_output_path):
            os.makedirs(self.srt_file_output_path)

    def extract_hard_subtitle(self, video_file_path: str, time_start: str="00:00", time_end: str=None, crop_x: int=None, crop_y: int=None,
                             crop_width: int=None, crop_height: int=None) -> str:
        if StringUtils.is_empty(time_end):
            video_duration = VideoUtils.get_video_duration(video_file_path)
            time_end = video_duration

        subtitle_content = get_subtitles(video_file_path, self.video, time_start, time_end, crop_x, crop_y, crop_width, crop_height)
        if self.enable_output_hard_subtitle_file:
            self.write_hard_subtitle_file(video_file_path, subtitle_content)
        return subtitle_content

    def write_hard_subtitle_file(self, video_file_path: str, srt_content: str, encoding: str = "utf-8") -> tuple[bool, str]:
        if StringUtils.is_empty(srt_content):
            return False, None
        video_file_path = StringUtils.replaceBackSlash(video_file_path)
        video_file_name = FileUtils.get_filename_without_suffix(video_file_path)
        srt_file_name = video_file_name + ".srt"
        srt_file_path = self.srt_file_output_path + srt_file_name
        write_result = save_subtitles_to_file(srt_content, srt_file_path, encoding)
        return write_result, srt_file_path

    def parse_subtitle_as_list(self, subtitle_content: str):
        if StringUtils.is_empty(subtitle_content):
            return False, []
        parse_result, hard_subtitle_list = SubtitleUtils.parse_srt_subtitle(subtitle_content)
        if parse_result:
            hard_subtitle_list = self.subtitle_deduplicate(hard_subtitle_list)
        return parse_result, hard_subtitle_list

    def subtitle_deduplicate(self, hard_subtitle_list):
        if hard_subtitle_list is None or len(hard_subtitle_list) <= 0:
            return None

        # 初始化结果列表，第一个元素直接放入
        dedup_list = [hard_subtitle_list[0].copy()]

        for current in hard_subtitle_list[1:]:
            last = dedup_list[-1]

            # 检查当前字幕是否与上一个字幕内容相同
            if current["subtitle"] == last["subtitle"]:
                # 合并时间范围：start_time取前者，end_time取后者
                last["end_time"] = current["end_time"]
                last["time_range"] = f"{last['start_time']} --> {current['end_time']}"
            else:
                # 不同则添加到结果列表
                dedup_list.append(current.copy())

        # 重新编号ID保持连续递增
        for idx, item in enumerate(dedup_list, start=1):
            item["id"] = idx

        return dedup_list


    def set_user_fullframe(self, user_fullframe: bool):
        if self.video is not None:
            self.video.set_user_fullframe(user_fullframe)

