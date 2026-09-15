"""
Utility helper functions for video processing.
"""

from typing import Dict, Any, Tuple
import os
import cv2


PRESETS: Dict[str, Dict[str, Any]] = {
    "subtle": {
        "brightness": 0.0,
        "contrast": 1.1,
        "sharpen": 0.3,
        "denoise": False,
        "saturation": 1.05,
        "auto_white_balance": False,
        "scale_factor": 1.0,
    },
    "balanced": {
        "brightness": 5.0,
        "contrast": 1.15,
        "sharpen": 0.5,
        "denoise": True,
        "denoise_d": 5,
        "saturation": 1.1,
        "auto_white_balance": False,
        "scale_factor": 1.0,
    },
    "vivid": {
        "brightness": 10.0,
        "contrast": 1.25,
        "sharpen": 0.8,
        "denoise": True,
        "denoise_d": 5,
        "saturation": 1.3,
        "auto_white_balance": True,
        "scale_factor": 1.0,
    },
    "hd_upscale": {
        "brightness": 5.0,
        "contrast": 1.15,
        "sharpen": 0.6,
        "denoise": True,
        "denoise_d": 5,
        "saturation": 1.1,
        "auto_white_balance": False,
        "scale_factor": 2.0,
        "upscale_method": "bicubic",
    },
}


def get_video_info(file_path: str) -> Dict[str, Any]:
    """
    Get metadata for a video file.

    :param file_path: Path to video file.
    :return: Dictionary containing video properties.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video file: {file_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

    cap.release()

    return {
        "file_path": file_path,
        "fps": fps,
        "width": width,
        "height": height,
        "frame_count": frame_count,
        "fourcc": fourcc,
        "duration_seconds": frame_count / fps if fps > 0 else 0.0,
    }


def select_fourcc_codec(output_path: str) -> int:
    """
    Select appropriate OpenCV FourCC codec based on output file extension.

    :param output_path: Output file path.
    :return: FourCC integer encoding.
    """
    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".mp4":
        return cv2.VideoWriter_fourcc(*"mp4v")
    elif ext == ".avi":
        return cv2.VideoWriter_fourcc(*"MJPG")
    elif ext in (".mkv", ".webm"):
        return cv2.VideoWriter_fourcc(*"VP80")
    else:
        return cv2.VideoWriter_fourcc(*"mp4v")
