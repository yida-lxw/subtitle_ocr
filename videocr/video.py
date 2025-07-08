from __future__ import annotations
import cv2
import numpy as np

from config.app_config import APPConfig
from utils.string_utils import StringUtils
from utils.video_utils import VideoUtils
from . import utils
from .models import PredictedFrames, PredictedSubtitle
from .opencv_adapter import Capture
from paddleocr import PaddleOCR


class Video:
    def __init__(self, app_config: APPConfig):
        self.app_config = app_config
        self.exclude_words = app_config.exclude_words
        # PaddleOCR模型文件目录
        paddle_model_base_dir = app_config.paddle_model_base_dir
        paddle_model_base_dir = StringUtils.replaceBackSlash(paddle_model_base_dir)
        paddle_model_base_dir = StringUtils.to_ends_with_back_slash(paddle_model_base_dir)
        self.paddle_model_base_dir = paddle_model_base_dir
        self.det_model_dir = f'{paddle_model_base_dir}PP-OCRv5_server_det'
        self.rec_model_dir = f'{paddle_model_base_dir}PP-OCRv5_server_rec'
        self.lang = self.app_config.ocr_language
        self.ocr_auto_rotate_image = self.app_config.ocr_auto_rotate_image
        self.use_device = self.app_config.use_device
        self.sim_threshold = self.app_config.sim_threshold
        self.conf_threshold = self.app_config.conf_threshold
        self.use_fullframe = self.app_config.use_fullframe
        self.brightness_threshold = self.app_config.brightness_threshold
        self.similar_image_threshold = self.app_config.similar_image_threshold
        self.similar_pixel_threshold = self.app_config.similar_pixel_threshold
        self.frames_to_skip = self.app_config.frames_to_skip
        self.enable_output_hard_subtitle_file = self.app_config.enable_output_hard_subtitle_file
        self.ocr = None
        self.init_paddle_ocr()

    def set_user_fullframe(self, user_fullframe: bool):
        self.use_fullframe = user_fullframe

    def get_user_fullframe(self):
        return self.use_fullframe

    def init_paddle_ocr(self):
        if utils.needs_conversion():
            if self.ocr is None:
                self.ocr = PaddleOCR(
                    lang=self.lang,
                    text_recognition_model_dir=self.rec_model_dir,
                    text_detection_model_dir=self.det_model_dir,
                    text_detection_model_name=utils.get_model_name_from_dir(self.det_model_dir),
                    text_recognition_model_name=utils.get_model_name_from_dir(self.rec_model_dir),
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_angle_cls=self.ocr_auto_rotate_image,
                    device=self.use_device
                )
        else:
            if self.ocr is None:
                self.ocr = PaddleOCR(
                    lang=self.lang,
                    rec_model_dir=self.rec_model_dir,
                    det_model_dir=self.det_model_dir,
                    use_gpu=True if "gpu" == self.use_device or "npu" == self.use_device else False
                )

    def run_ocr(self, video_file_path:str, time_start: str, time_end: str, crop_x: int, crop_y: int, crop_width: int, crop_height: int) -> None:
        # self.num_frames = VideoUtils.get_video_frame_count(video_file_path, self.app_config.ffmpeg_path)
        # video_info = VideoUtils.get_video_info(video_file_path, self.app_config.ffmpeg_path)
        # self.fps = video_info["fps"]
        # self.height = video_info["height"]
        with Capture(video_file_path) as v:
            self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = v.get(cv2.CAP_PROP_FPS)
            self.height = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))


        conf_threshold_percent = float(self.conf_threshold/100)
        self.pred_frames = []

        ocr_start = utils.get_frame_index(time_start, self.fps) if time_start else 0
        ocr_end = utils.get_frame_index(time_end, self.fps) if time_end else self.num_frames

        if ocr_end < ocr_start:
            raise ValueError('time_start is later than time_end')
        num_ocr_frames = ocr_end - ocr_start

        crop_x_end = None
        crop_y_end = None
        if crop_x is not None and crop_y is not None and crop_width and crop_height:
            crop_x_end = crop_x + crop_width
            crop_y_end = crop_y + crop_height

        # get frames from ocr_start to ocr_end
        with Capture(video_file_path) as v:
            v.set(cv2.CAP_PROP_POS_FRAMES, ocr_start)
            prev_grey = None
            predicted_frames = None
            modulo = self.frames_to_skip + 1
            for i in range(num_ocr_frames):
                if i % modulo == 0:
                    frame = v.read()[1]
                    if frame is None:
                        continue
                    if not self.use_fullframe:
                        if crop_x_end and crop_y_end:
                            frame = frame[crop_y:crop_y_end, crop_x:crop_x_end]
                        else:
                            # only use bottom third of the frame by default
                            frame = frame[2 * self.height // 3:, :]

                    if self.brightness_threshold:
                        frame = cv2.bitwise_and(frame, frame, mask=cv2.inRange(frame, (self.brightness_threshold, self.brightness_threshold, self.brightness_threshold), (255, 255, 255)))

                    if self.similar_image_threshold:
                        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        if prev_grey is not None:
                            _, absdiff = cv2.threshold(cv2.absdiff(prev_grey, grey), self.similar_pixel_threshold, 255, cv2.THRESH_BINARY)
                            if np.count_nonzero(absdiff) < self.similar_image_threshold:
                                predicted_frames.end_index = i + ocr_start
                                prev_grey = grey
                                continue

                        prev_grey = grey

                    predicted_frames = PredictedFrames(i + ocr_start, self.ocr.ocr(frame), conf_threshold_percent)
                    self.pred_frames.append(predicted_frames)
                else:
                    v.read()
        

    def get_subtitles(self, sim_threshold: int) -> str:
        self._generate_subtitles(sim_threshold)
        return ''.join(
            '{}\n{} --> {}\n{}\n\n'.format(
                i,
                utils.get_srt_timestamp(sub.index_start, self.fps),
                utils.get_srt_timestamp(sub.index_end + 1, self.fps),
                sub.text)
            for i, sub in enumerate(self.pred_subs, start=1))

    def _generate_subtitles(self, sim_threshold: int) -> None:
        self.pred_subs = []

        if self.pred_frames is None:
            raise AttributeError(
                'Please call self.run_ocr() first to perform ocr on frames')

        max_frame_merge_diff = int(0.09 * self.fps)
        for frame in self.pred_frames:
            self._append_sub(PredictedSubtitle([frame], sim_threshold), max_frame_merge_diff)
        self.pred_subs = [sub for sub in self.pred_subs if len(sub.frames[0].lines) > 0]

    def _append_sub(self, sub: PredictedSubtitle, max_frame_merge_diff: int) -> None:
        if len(sub.frames) == 0:
            return

        # merge new sub to the last subs if they are not empty, similar and within 0.09 seconds apart
        if self.pred_subs:
            last_sub = self.pred_subs[-1]
            if len(last_sub.frames[0].lines) > 0 and sub.index_start - last_sub.index_end <= max_frame_merge_diff and last_sub.is_similar_to(sub):
                del self.pred_subs[-1]
                sub = PredictedSubtitle(last_sub.frames + sub.frames, sub.sim_threshold)


        if StringUtils.is_not_empty(sub.text):
            sub.text = self.remove_exclude_words(sub.text)
            if StringUtils.is_not_empty(sub.text) and "\n" in sub.text:
                text_array = sub.text.split("\n")
                text_first = text_array[0]
                text_second = text_array[1]

                if StringUtils.is_alphanumeric(text_first):
                    sub.text = text_second
                else:
                    sub.text = text_first + "," + text_second


        if StringUtils.is_not_empty(sub.text):
            self.pred_subs.append(sub)

    def remove_exclude_words(self, text):
        if self.exclude_words is None or len(self.exclude_words) <= 0:
            return text
        if StringUtils.is_empty(text):
            return None
        if text in self.exclude_words:
            return None

        if StringUtils.is_letter_number_or_punctuation(text):
            return None

        if "\n" in text:
            text_array = text.split("\n")
            text_first = text_array[0]
            text_second = text_array[1]
            if text_first in self.exclude_words or StringUtils.is_letter_number_or_punctuation(text_first):
                text_first = ""
            if text_second in self.exclude_words or StringUtils.is_letter_number_or_punctuation(text_second):
                text_second = ""

            if StringUtils.is_empty(text_first) and StringUtils.is_empty(text_second):
                return None
            if StringUtils.is_empty(text_first):
                return text_second
            if StringUtils.is_empty(text_second):
                return text_first
            return text_first + "\n" + text_second

        elif "," in text:
            text_array = text.split(",")
            text_first = text_array[0]
            text_second = text_array[1]
            if text_first in self.exclude_words or StringUtils.is_letter_number_or_punctuation(text_first):
                text_first = ""
            if text_second in self.exclude_words or StringUtils.is_letter_number_or_punctuation(text_second):
                text_second = ""

            if StringUtils.is_empty(text_first) and StringUtils.is_empty(text_second):
                return None
            if StringUtils.is_empty(text_first):
                return text_second
            if StringUtils.is_empty(text_second):
                return text_first
            return text_first + "," + text_second

        elif " " in text:
            text_array = text.split(" ")
            text_first = text_array[0]
            text_second = text_array[1]
            if text_first in self.exclude_words or StringUtils.is_letter_number_or_punctuation(text_first):
                text_first = ""
            if text_second in self.exclude_words or StringUtils.is_letter_number_or_punctuation(text_second):
                text_second = ""

            if StringUtils.is_empty(text_first) and StringUtils.is_empty(text_second):
                return None
            if StringUtils.is_empty(text_first):
                return text_second
            if StringUtils.is_empty(text_second):
                return text_first
            return text_first + " " + text_second
        else:
            return text




