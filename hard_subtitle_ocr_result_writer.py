from config.app_config import APPConfig
from db_pool import SQLTemplate
from status_constants import save_image_subtitle_ocr_success, save_image_subtitle_ocr_failed, image_subtitle_ocr_failed, \
    image_subtitle_ocr_no_data, image_subtitle_area_predict_failed, image_subtitle_area_predict_box_invalid, \
    image_subtitle_area_croped_failed
from utils.string_utils import StringUtils

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

# 加载配置文件
app_config_path = "config/app.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)
table_name = app_config_loaded.video_hard_subtitle_ocr_table_name

create_table_sql_tpl = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id  TEXT NOT NULL,
            file_hash  TEXT NOT NULL,
            subtitle_content  TEXT NOT NULL
        );
    """

count_sql = f"select count(*) from {table_name} where file_hash = ?"
select_sql = f"SELECT * FROM {table_name} WHERE file_hash = ? limit 1"
insert_sql = f"INSERT OR IGNORE INTO {table_name}(task_id, file_hash, subtitle_content) VALUES (?,?,?)"
update_sql = f"UPDATE {table_name} SET task_id=?, subtitle_content=? WHERE file_hash=?"

class HardSubtitleOcrResultInfo:
    def __init__(self, task_id: str, file_hash:str, subtitle_content:str):
        self.task_id = task_id
        self.file_hash = file_hash
        self.subtitle_content = subtitle_content

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "file_hash": self.file_hash,
            "subtitle_content": self.subtitle_content
        }

class HardSubtitleOcrResultWriter:

    def __init__(self, sql_template: SQLTemplate):
        self.sql_template = sql_template

    def create_table(self):
        create_table_sql = create_table_sql_tpl.replace("${table_name}", table_name)
        create_result = self.sql_template.create_table(create_table_sql)
        create_result_text = "成功" if create_result else "失败"
        print(f"SQLLite表{table_name}创建{create_result_text}")

    def load_hard_subtitle(self, file_hash: str):
        hard_subtitle_info = self.sql_template.find_one(select_sql, args=(file_hash,))
        return hard_subtitle_info

    def save_ocr_result(self, hard_subtitle_ocr_result_info: HardSubtitleOcrResultInfo) -> bool:
        if hard_subtitle_ocr_result_info is None:
            return False
        print("开始保存video_hard_subtitle_ocr_result")
        task_id = hard_subtitle_ocr_result_info.task_id
        file_hash = hard_subtitle_ocr_result_info.file_hash
        subtitle_content = hard_subtitle_ocr_result_info.subtitle_content

        save_result = self.sql_template.find_one(select_sql, (file_hash,))
        data_json = StringUtils.to_json_str(hard_subtitle_ocr_result_info.to_dict())
        print(f"insert-sql:{insert_sql},params:\n{data_json}")
        if save_result is None or len(save_result) <= 0:
            effect_row = self.sql_template.insert(insert_sql, return_id=False, args=(task_id, file_hash,subtitle_content))
        else:
            effect_row = self.sql_template.update(update_sql, args=(task_id,subtitle_content, file_hash))
        return effect_row > 0


    # 判断当前文件的硬字幕数据是否已经存在
    def hard_subtitle_exists(self, file_hash: str):
        image_subtitle_ocr_matched_count = self.sql_template.query_count(count_sql, args=(file_hash,))
        return image_subtitle_ocr_matched_count > 0



