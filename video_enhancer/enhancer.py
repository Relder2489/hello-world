"""
Main video enhancer engine class.
"""

from typing import Optional, Callable, Dict, Any
import os
import cv2

from video_enhancer import filters
from video_enhancer.utils import get_video_info, select_fourcc_codec, PRESETS


class VideoEnhancer:
    """
    VideoEnhancer processes video files frame-by-frame applying configured filters.
    """

    def __init__(
        self,
        brightness: float = 0.0,
        contrast: float = 1.0,
        sharpen_factor: float = 0.0,
        enable_denoise: bool = False,
        denoise_d: int = 5,
        saturation: float = 1.0,
        enable_auto_wb: bool = False,
        scale_factor: float = 1.0,
        upscale_method: str = "bicubic",
    ):
        self.brightness = brightness
        self.contrast = contrast
        self.sharpen_factor = sharpen_factor
        self.enable_denoise = enable_denoise
        self.denoise_d = denoise_d
        self.saturation = saturation
        self.enable_auto_wb = enable_auto_wb
        self.scale_factor = scale_factor
        self.upscale_method = upscale_method

    @classmethod
    def from_preset(cls, preset_name: str, **overrides) -> "VideoEnhancer":
        """
        Instantiate VideoEnhancer from a preset configuration.

        :param preset_name: Name of preset ('subtle', 'balanced', 'vivid', 'hd_upscale')
        :param overrides: Kwargs to override preset defaults.
        :return: VideoEnhancer instance
        """
        if preset_name not in PRESETS:
            raise ValueError(f"Unknown preset '{preset_name}'. Options: {list(PRESETS.keys())}")

        config = PRESETS[preset_name].copy()
        # Map preset keys to init parameter names if needed
        params = {
            "brightness": config.get("brightness", 0.0),
            "contrast": config.get("contrast", 1.0),
            "sharpen_factor": config.get("sharpen", 0.0),
            "enable_denoise": config.get("denoise", False),
            "denoise_d": config.get("denoise_d", 5),
            "saturation": config.get("saturation", 1.0),
            "enable_auto_wb": config.get("auto_white_balance", False),
            "scale_factor": config.get("scale_factor", 1.0),
            "upscale_method": config.get("upscale_method", "bicubic"),
        }
        params.update(overrides)
        return cls(**params)

    def process_frame(self, frame) -> Any:
        """
        Apply all configured enhancement filters to a single frame.

        :param frame: BGR frame array
        :return: Enhanced BGR frame array
        """
        out = frame.copy()

        if self.enable_auto_wb:
            out = filters.auto_white_balance(out)

        if self.brightness != 0.0 or self.contrast != 1.0:
            out = filters.adjust_brightness_contrast(out, brightness=self.brightness, contrast=self.contrast)

        if self.saturation != 1.0:
            out = filters.adjust_saturation(out, saturation=self.saturation)

        if self.enable_denoise:
            out = filters.denoise(out, d=self.denoise_d)

        if self.sharpen_factor > 0:
            out = filters.sharpen(out, factor=self.sharpen_factor)

        if self.scale_factor != 1.0:
            out = filters.upscale(out, scale_factor=self.scale_factor, method=self.upscale_method)

        return out

    def process_video(
        self,
        input_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        max_frames: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Enhance input video file and write output file.

        :param input_path: Input video file path.
        :param output_path: Output video file path.
        :param progress_callback: Optional function (current_frame, total_frames) -> None.
        :param max_frames: Optional maximum number of frames to process.
        :return: Dictionary with processing statistics.
        """
        info = get_video_info(input_path)
        cap = cv2.VideoCapture(input_path)

        fps = info["fps"]
        orig_w = info["width"]
        orig_h = info["height"]
        total_frames = info["frame_count"]

        if max_frames and max_frames < total_frames:
            target_frames = max_frames
        else:
            target_frames = total_frames

        out_w = int(round(orig_w * self.scale_factor))
        out_h = int(round(orig_h * self.scale_factor))

        fourcc = select_fourcc_codec(output_path)
        writer = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

        if not writer.isOpened():
            cap.release()
            raise RuntimeError(f"Could not open VideoWriter for output file: {output_path}")

        frames_processed = 0
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                enhanced = self.process_frame(frame)
                writer.write(enhanced)

                frames_processed += 1
                if progress_callback:
                    progress_callback(frames_processed, target_frames)

                if max_frames and frames_processed >= max_frames:
                    break

        finally:
            cap.release()
            writer.release()

        return {
            "input_path": input_path,
            "output_path": output_path,
            "frames_processed": frames_processed,
            "fps": fps,
            "output_resolution": (out_w, out_h),
        }
