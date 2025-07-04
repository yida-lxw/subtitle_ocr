# -*- coding: utf-8 -*-
import os

import yaml
from yaml import YAMLError

from object_iterator import ObjectIterator, IteratorType
from utils.string_utils import StringUtils

class APPConfigError(Exception):
    """自定义配置异常类"""
    pass


class APPConfig:
    def __init__(self,
                 host: str,
                 port: int,
                 model_path: str,
                 paddle_model_base_dir: str,
                 work_dir: str,
                 ffmpeg_path: str,
                 upload_relative_dir: str,
                 workers=4,
                 predict_min_score: float = 0.60,
                 output_predict_image: bool = False,
                 delete_original_image_after_predict: bool = False,
                 extracted_frames_relative_dir: str = "extracted_frames",
                 croped_images_relative_dir: str = "croped_images",
                 hard_subtitle_output_folder: str = "hard_srts",
                 enable_output_hard_subtitle_file:bool = False,
                 extracted_soft_subtitles_dir: str = "extracted_soft_subtitles",
                 video_hard_subtitle_ocr_table_name: str = "video_hard_subtitle_ocr_result",
                 use_device:str = "cpu",
                 use_fullframe: bool= False,
                 frames_to_skip: int = 1,
                 sim_threshold: int = 80,
                 conf_threshold: int = 75,
                 brightness_threshold: int = 210,
                 similar_image_threshold: int = 1000,
                 similar_pixel_threshold: int = 25,
                 ocr_auto_rotate_image:bool = False,
                 ocr_language:str = "ch",
                 kv_cache_max_size: int = 100000,
                 kv_cache_max_age: int = 3600,
                 enable_subtitle_cache: bool = False,
                 exclude_words: list = None
                 ):

        # 核心配置项
        self.host = host
        self.port = port
        self.workers = workers
        self.model_path = model_path
        self.paddle_model_base_dir = paddle_model_base_dir
        self.predict_min_score = predict_min_score
        self.output_predict_image = output_predict_image
        self.delete_original_image_after_predict = delete_original_image_after_predict
        self.work_dir = work_dir
        self.ffmpeg_path = ffmpeg_path
        self.upload_relative_dir = upload_relative_dir
        self.extracted_frames_relative_dir = extracted_frames_relative_dir
        self.croped_images_relative_dir = croped_images_relative_dir
        self.hard_subtitle_output_folder = hard_subtitle_output_folder
        self.enable_output_hard_subtitle_file = enable_output_hard_subtitle_file
        self.extracted_soft_subtitles_dir = extracted_soft_subtitles_dir
        self.video_hard_subtitle_ocr_table_name = video_hard_subtitle_ocr_table_name
        self.use_device = use_device
        self.use_fullframe = use_fullframe
        self.frames_to_skip = frames_to_skip
        self.sim_threshold = sim_threshold
        self.conf_threshold = conf_threshold
        self.brightness_threshold = brightness_threshold
        self.similar_image_threshold = similar_image_threshold
        self.similar_pixel_threshold = similar_pixel_threshold
        self.ocr_auto_rotate_image = ocr_auto_rotate_image
        self.ocr_language = ocr_language
        self.kv_cache_max_size = kv_cache_max_size
        self.kv_cache_max_age = kv_cache_max_age
        self.enable_subtitle_cache = enable_subtitle_cache
        self.exclude_words = exclude_words

    @classmethod
    def load(cls, file_path='config/app.yml'):
        if not StringUtils.is_absolute_path(file_path):
            project_basepath = StringUtils.get_project_basepath()
            project_basepath = StringUtils.replaceBackSlash(project_basepath)
            project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)
            file_path = StringUtils.replaceBackSlash(file_path)
            file_path = project_basepath +  file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            raise APPConfigError(f"配置文件 {file_path} 未找到")
        except YAMLError as e:
            raise APPConfigError(f"YAML解析错误: {e}")

        app_config = config_data.get('app')
        if not app_config:
            raise APPConfigError("配置文件中缺少 'app'配置项")

        # 验证必需字段（新增predict_min_score和调整字段名）
        required_fields = [
            'host', 'port', 'paddle_model_base_dir', 'work_dir', 'ffmpeg_path'
        ]
        missing_fields = [field for field in required_fields if field not in app_config]
        if missing_fields:
            raise APPConfigError(f"缺少必需字段: {', '.join(missing_fields)}")

        if not isinstance(app_config['paddle_model_base_dir'], str):
            raise APPConfigError("paddle_model_base_dir必须为字符串类型")

        # 类型验证（新增浮点数验证）
        if not isinstance(app_config['predict_min_score'], float):
            raise APPConfigError("predict_min_score必须为浮点数类型")

        # 创建配置对象（参数对应调整）
        return cls(
            host=app_config['host'],
            port=app_config['port'],
            model_path=app_config['model_path'],
            paddle_model_base_dir=app_config['paddle_model_base_dir'],
            work_dir=app_config['work_dir'],
            ffmpeg_path=app_config['ffmpeg_path'],
            upload_relative_dir=app_config['upload_relative_dir'],
            extracted_frames_relative_dir=app_config["extracted_frames_relative_dir"],
            croped_images_relative_dir=app_config["croped_images_relative_dir"],
            hard_subtitle_output_folder=app_config['hard_subtitle_output_folder'],
            enable_output_hard_subtitle_file=app_config['enable_output_hard_subtitle_file'],
            extracted_soft_subtitles_dir=app_config["extracted_soft_subtitles_dir"],
            video_hard_subtitle_ocr_table_name=app_config["video_hard_subtitle_ocr_table_name"],
            workers=app_config["workers"],
            predict_min_score=app_config['predict_min_score'],
            output_predict_image=app_config['output_predict_image'],
            delete_original_image_after_predict=app_config['delete_original_image_after_predict'],
            ocr_auto_rotate_image=app_config["ocr_auto_rotate_image"],
            ocr_language=app_config["ocr_language"],
            use_device=app_config["use_device"],
            use_fullframe=app_config["use_fullframe"],
            frames_to_skip=app_config["frames_to_skip"],
            sim_threshold=app_config['sim_threshold'],
            conf_threshold=app_config['conf_threshold'],
            brightness_threshold=app_config['brightness_threshold'],
            similar_image_threshold=app_config['similar_image_threshold'],
            similar_pixel_threshold=app_config['similar_pixel_threshold'],
            kv_cache_max_size=app_config["kv_cache_max_size"],
            kv_cache_max_age=app_config["kv_cache_max_age"],
            enable_subtitle_cache=app_config["enable_subtitle_cache"],
            exclude_words=app_config["exclude_words"],
        )


    @staticmethod
    def load_app_config(project_basepath=None, config_path="config/app.yml"):
        if StringUtils.is_empty(project_basepath):
            project_basepath = StringUtils.get_project_basepath()
        project_basepath = StringUtils.replaceBackSlash(project_basepath)
        project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)
        app_yml_file_path = os.path.join(project_basepath, config_path)
        return APPConfig.load(file_path=app_yml_file_path)

    def __iter__(self):
        field_dict = self.__dict__
        final_field_dict = {}
        final_field_keys = []
        for key, value in field_dict.items():
            if type(value) == IteratorType:
                continue
            final_field_keys.append(key)
            final_field_dict.update({key: value})
        return ObjectIterator(field_dict=final_field_dict, field_keys=final_field_keys, iteratorType=self.iteratorType)

    def getHost(self):
        return self.host

    def setHost(self, host: str):
        self.host = host
        return self

    def getPort(self):
        return self.port

    def setPort(self, port: int):
        self.port = port
        return self

    def getWorkers(self):
        return self.workers

    def setWorkers(self, workers: int):
        self.workers = workers
        return self
    def getModelPath(self):
        return self.model_path
    def setModelPath(self, model_path: str):
        self.model_path = model_path
        return self

    def getWorkDir(self):
        return self.work_dir
    def setWorkDir(self, work_dir: str):
        self.work_dir = work_dir
        return self
    def getUploadRelativeDir(self):
        return self.upload_relative_dir
    def setUploadRelativeDir(self, upload_relative_dir: str):
        self.upload_relative_dir = upload_relative_dir
        return self
    def getExtractedFramesRelativeDir(self):
        return self.extracted_frames_relative_dir
    def setExtractedFramesRelativeDir(self, extracted_frames_relative_dir: str):
        self.extracted_frames_relative_dir = extracted_frames_relative_dir
        return self
    def getCropedImagesRelativeDir(self):
        return self.croped_images_relative_dir
    def setCropedImagesRelativeDir(self, croped_images_relative_dir: str):
        self.croped_images_relative_dir = croped_images_relative_dir
        return self

    def getExtractedSoftSubtitlesDir(self):
        return self.extracted_soft_subtitles_dir

    def setExtractedSoftSubtitlesDir(self, extracted_soft_subtitles_dir: str):
        self.extracted_soft_subtitles_dir = extracted_soft_subtitles_dir
        return self

    def getPredictMinScore(self):
        return self.predict_min_score
    def setPredictMinScore(self, predict_min_score: float):
        self.predict_min_score = predict_min_score
        return self
    def getOutputPredictImage(self):
        return self.output_predict_image
    def setOutputPredictImage(self, output_predict_image: bool):
        self.output_predict_image = output_predict_image
        return self
    def getDeleteOriginalImageAfterPredict(self):
        return self.delete_original_image_after_predict
    def setDeleteOriginalImageAfterPredict(self, delete_original_image_after_predict: bool):
        self.delete_original_image_after_predict = delete_original_image_after_predict
        return self

    def getOcrAutoRotateImage(self):
        return self.ocr_auto_rotate_image
    def setOcrAutoRotateImage(self, ocr_auto_rotate_image: bool):
        self.ocr_auto_rotate_image = ocr_auto_rotate_image
        return self
    def getOcrLanguage(self):
        return self.ocr_language
    def setOcrLanguage(self, ocr_language: str):
        self.ocr_language = ocr_language
        return self


    def __eq__(self, other):
        if isinstance(other, APPConfig):
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in self.__dict__
                if not attr.startswith('_')
            )
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    
