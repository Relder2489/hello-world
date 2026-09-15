"""
Frame filter module for video enhancement.
Provides individual image processing functions operating on BGR numpy arrays.
"""

import cv2
import numpy as np


def adjust_brightness_contrast(frame: np.ndarray, brightness: float = 0.0, contrast: float = 1.0) -> np.ndarray:
    """
    Adjust brightness and contrast of a video frame.

    :param frame: Input image frame in BGR format.
    :param brightness: Brightness offset (-100 to 100).
    :param contrast: Contrast scaling factor (> 0, e.g. 1.0 is neutral, 1.5 is +50%).
    :return: Processed image frame.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid image frame provided.")
    if contrast < 0:
        raise ValueError("Contrast factor must be non-negative.")

    return cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)


def sharpen(frame: np.ndarray, factor: float = 0.5) -> np.ndarray:
    """
    Sharpen an image frame using unsharp masking.

    :param frame: Input image frame in BGR format.
    :param factor: Sharpening intensity factor (0.0 to 3.0).
    :return: Processed image frame.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid image frame provided.")
    if factor <= 0:
        return frame.copy()

    blurred = cv2.GaussianBlur(frame, (0, 0), sigmaX=3)
    sharpened = cv2.addWeighted(frame, 1.0 + factor, blurred, -factor, 0)
    return sharpened


def denoise(frame: np.ndarray, d: int = 5, sigma_color: float = 75.0, sigma_space: float = 75.0) -> np.ndarray:
    """
    Apply bilateral filtering to remove noise while preserving edges.

    :param frame: Input image frame in BGR format.
    :param d: Diameter of each pixel neighborhood.
    :param sigma_color: Filter sigma in the color space.
    :param sigma_space: Filter sigma in the coordinate space.
    :return: Processed image frame.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid image frame provided.")
    if d <= 0:
        return frame.copy()

    return cv2.bilateralFilter(frame, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)


def adjust_saturation(frame: np.ndarray, saturation: float = 1.0) -> np.ndarray:
    """
    Adjust saturation level of an image frame.

    :param frame: Input image frame in BGR format.
    :param saturation: Saturation multiplier factor (1.0 is neutral).
    :return: Processed image frame.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid image frame provided.")
    if saturation < 0:
        raise ValueError("Saturation factor must be non-negative.")
    if saturation == 1.0:
        return frame.copy()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def auto_white_balance(frame: np.ndarray) -> np.ndarray:
    """
    Apply Gray World auto white balance algorithm to normalise color channels.

    :param frame: Input image frame in BGR format.
    :return: Processed image frame.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid image frame provided.")

    b, g, r = cv2.split(frame.astype(np.float32))
    mean_b, mean_g, mean_r = np.mean(b), np.mean(g), np.mean(r)

    # Avoid divide-by-zero
    if mean_b == 0 or mean_g == 0 or mean_r == 0:
        return frame.copy()

    gray_mean = (mean_b + mean_g + mean_r) / 3.0
    scale_b = gray_mean / mean_b
    scale_g = gray_mean / mean_g
    scale_r = gray_mean / mean_r

    b = np.clip(b * scale_b, 0, 255)
    g = np.clip(g * scale_g, 0, 255)
    r = np.clip(r * scale_r, 0, 255)

    balanced = cv2.merge([b, g, r]).astype(np.uint8)
    return balanced


def upscale(frame: np.ndarray, scale_factor: float = 2.0, method: str = "bicubic") -> np.ndarray:
    """
    Upscale an image frame by a scale factor.

    :param frame: Input image frame in BGR format.
    :param scale_factor: Scaling factor (> 0).
    :param method: Interpolation method ('bicubic', 'lanczos', 'linear', 'nearest').
    :return: Processed image frame.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Invalid image frame provided.")
    if scale_factor <= 0:
        raise ValueError("Scale factor must be positive.")
    if scale_factor == 1.0:
        return frame.copy()

    methods = {
        "bicubic": cv2.INTER_CUBIC,
        "lanczos": cv2.INTER_LANCZOS4,
        "linear": cv2.INTER_LINEAR,
        "nearest": cv2.INTER_NEAREST,
    }

    interp_flag = methods.get(method.lower())
    if interp_flag is None:
        raise ValueError(f"Unsupported interpolation method '{method}'. Choice of: {list(methods.keys())}")

    height, width = frame.shape[:2]
    new_width = int(round(width * scale_factor))
    new_height = int(round(height * scale_factor))

    return cv2.resize(frame, (new_width, new_height), interpolation=interp_flag)
