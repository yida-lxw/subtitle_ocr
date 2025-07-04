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
table_name = app_config_loaded.image_ocr_status_table_name
image_subtitle_ocr_table_name = app_config_loaded.image_subtitle_ocr_table_name

create_table_sql_tpl = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id  TEXT NOT NULL,
            frame_time  TEXT NOT NULL,
            frame_index  INTEGER NOT NULL,
            ocr_status  TEXT NOT NULL,
            file_hash  TEXT NOT NULL,
            file_name  TEXT NOT NULL,
            image_total_count INTEGER NOT NULL
        );
    """

select_sql = f"SELECT * FROM {table_name} WHERE file_hash = ? and frame_index = ?"
insert_sql = f"INSERT OR IGNORE INTO {table_name}(task_id, frame_time, frame_index, ocr_status, file_hash, file_name,image_total_count) VALUES (?,?,?,?,?,?,?)"
update_sql = f"UPDATE {table_name} SET frame_time=?, frame_index=?,ocr_status=?,file_name=? WHERE file_hash=?"

class SubtitleOCRStatusInfo:
    def __init__(self, task_id: str, frame_time:str, frame_index:int, ocr_status:str, file_hash:str, file_name:str, image_total_count:int):
        self.task_id = task_id
        self.frame_time = frame_time
        self.frame_index = frame_index
        self.ocr_status = ocr_status
        self.file_hash = file_hash
        self.file_name = file_name
        self.image_total_count = image_total_count

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "frame_time": self.frame_time,
            "frame_index": self.frame_index,
            "ocr_status": self.ocr_status,
            "file_hash": self.file_hash,
            "file_name": self.file_name,
            "image_total_count": self.image_total_count
        }

class SubtitleOCRStatusWriter:

    def __init__(self, sql_template: SQLTemplate, file_hash:str, image_total_count:int):
        self.sql_template = sql_template
        self.file_hash = file_hash
        self.image_total_count = image_total_count

    def create_table(self):
        create_table_sql = create_table_sql_tpl.replace("${table_name}", table_name)
        create_result = self.sql_template.create_table(create_table_sql)
        create_result_text = "成功" if create_result else "失败"
        print(f"SQLLite表{table_name}创建{create_result_text}")

    def save_ocr_status_result(self, subtitleOcrStatusInfo: SubtitleOCRStatusInfo) -> bool:
        if subtitleOcrStatusInfo is None:
            return False
        print("开始保存image_ocr_status")
        task_id = subtitleOcrStatusInfo.task_id
        frame_time = subtitleOcrStatusInfo.frame_time
        frame_index = subtitleOcrStatusInfo.frame_index
        ocr_status = subtitleOcrStatusInfo.ocr_status
        file_hash = subtitleOcrStatusInfo.file_hash
        file_name = subtitleOcrStatusInfo.file_name
        image_total_count = subtitleOcrStatusInfo.image_total_count
        subtitle_ocr_status_result = self.sql_template.find_one(select_sql, (file_hash,frame_index))
        data_json = StringUtils.to_json_str(subtitleOcrStatusInfo.to_dict())
        print(f"insert-sql:{insert_sql},params:\n{data_json}")
        if subtitle_ocr_status_result is None or len(subtitle_ocr_status_result) <= 0:
            effect_row = self.sql_template.insert(insert_sql, return_id=False, args=(task_id, frame_time, frame_index,
                                                                                     ocr_status, file_hash, file_name,
                                                                                     image_total_count))
        else:
            effect_row = self.sql_template.update(update_sql, args=(frame_time, frame_index,ocr_status,file_name, file_hash))
        return effect_row > 0


    # 判断是否每张图片的OCR都支持成功了(OCR识别成功但提取到的字幕文本为空的除非)
    def is_all_complete(self):
        count_sql = f"select count(*) from {image_subtitle_ocr_table_name} where file_hash = ?"
        image_subtitle_ocr_matched_count = self.sql_template.query_count(count_sql, args=(self.file_hash,))
        save_subtitle_success_count = self.get_save_subtitle_success_count()

        return image_subtitle_ocr_matched_count == save_subtitle_success_count

    # 判断是否存在图片OCR处理失败情况
    def exists_error_status(self):
        count_sql = f"select count(*) from {table_name} where file_hash = ? and ocr_status in (?,?)"
        matched_count = self.sql_template.query_count(count_sql,
                                                      args=(self.file_hash, save_image_subtitle_ocr_failed, image_subtitle_ocr_failed))
        return matched_count > 0

    # 获取字幕状态数据总条数
    def get_total_records_count(self):
        count_sql = f"select count(*) from {table_name} where file_hash = ?"
        matched_count = self.sql_template.query_count(count_sql, args=(self.file_hash,))
        return matched_count

    # 获取字幕保存成功的条数
    def get_save_subtitle_success_count(self):
        ocr_status = save_image_subtitle_ocr_success
        count_sql = f"select count(*) from {table_name} where file_hash = ? and ocr_status=?"
        matched_count = self.sql_template.query_count(count_sql, args=(self.file_hash, ocr_status))
        return matched_count

    # 获取OCR执行成功但没有字幕的帧
    def get_no_data_of_frames(self):
        ocr_status = image_subtitle_ocr_no_data
        query_sql = f"select * from {table_name} where file_hash = ? and ocr_status=? order by frame_index"
        matched_result = self.sql_template.find_many(query_sql, args=(self.file_hash, ocr_status))
        return matched_result

    # 获取OCR执行成功但没有字幕的帧的数量
    def get_no_data_of_frames_count(self):
        ocr_status = image_subtitle_ocr_no_data
        query_count_sql = f"select count(*) from {table_name} where file_hash = ? and ocr_status=?"
        matched_count = self.sql_template.query_count(query_count_sql, args=(self.file_hash, ocr_status))
        return matched_count

    # 获取视频区域预测失败的视频帧数量
    def get_predict_failed_frames_count(self):
        ocr_status = image_subtitle_area_predict_failed
        query_count_sql = f"select count(*) from {table_name} where file_hash = ? and ocr_status=?"
        matched_count = self.sql_template.query_count(query_count_sql, args=(self.file_hash, ocr_status))
        return matched_count

    # 获取视频区域预测框不合法的视频帧数量
    def get_predict_box_invalid_frames_count(self):
        ocr_status = image_subtitle_area_predict_box_invalid
        query_count_sql = f"select count(*) from {table_name} where file_hash = ? and ocr_status=?"
        matched_count = self.sql_template.query_count(query_count_sql, args=(self.file_hash, ocr_status))
        return matched_count

    # 获取视频区域裁剪失败的视频帧数量
    def get_predict_box_crop_failed_frames_count(self):
        ocr_status = image_subtitle_area_croped_failed
        query_count_sql = f"select count(*) from {table_name} where file_hash = ? and ocr_status=?"
        matched_count = self.sql_template.query_count(query_count_sql, args=(self.file_hash, ocr_status))
        return matched_count

    # 获取OCR执行成功的所有视频帧
    def load_frames_for_ocr_success(self):
        ocr_status = save_image_subtitle_ocr_success
        query_sql = f"select * from {table_name} where file_hash = ? and ocr_status=? order by frame_index"
        matched_result = self.sql_template.find_many(query_sql, args=(self.file_hash, ocr_status))
        return matched_result

    def get_total_image_count(self, file_hash:str):
        query_sql = f"SELECT image_total_count FROM {table_name} WHERE file_hash=?"
        return self.sql_template.query_count(query_sql, (file_hash,))

    def set_total_image_count(self, image_total_count:int):
        self.image_total_count = image_total_count

