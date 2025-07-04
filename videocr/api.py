from utils.string_utils import StringUtils
from .video import Video


def get_subtitles(video_file_path: str, v:Video, time_start:str='0:00', time_end:str='', crop_x=None, crop_y=None,
                  crop_width=None, crop_height=None) -> str:
    v.run_ocr(video_file_path, time_start, time_end, crop_x, crop_y, crop_width, crop_height)
    return v.get_subtitles(v.sim_threshold)


def save_subtitles_to_file(subtitle_content: str, srt_file_path:str, encoding:str="utf-8") -> bool:
    if StringUtils.is_empty(subtitle_content):
        return False
    try:
        with open(srt_file_path, 'w+', encoding=encoding) as f:
            f.write(subtitle_content)
        return True
    except:
        return False
