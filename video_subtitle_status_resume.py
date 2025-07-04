from config.app_config import APPConfig
from db_pool import SQLTemplate


delete_sql_for_video_hard_subtitle_ocr_result = "delete from video_hard_subtitle_ocr_result where file_hash = ?"

class VideoSubtitleStatusResume:
    def __init__(self, app_config: APPConfig, sql_template: SQLTemplate, kv_cache):
        self.app_config = app_config
        self.sql_template = sql_template
        self.kv_cache = kv_cache

    def resume(self, file_hash: str):
        self.sql_template.delete(delete_sql_for_video_hard_subtitle_ocr_result, (file_hash,))

    def clean_cache(self, file_hash: str):
        self.kv_cache.set(file_hash, [])