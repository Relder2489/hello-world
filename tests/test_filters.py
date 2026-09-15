import pytest
import numpy as np
import cv2

from video_enhancer.filters import (
    adjust_brightness_contrast,
    sharpen,
    denoise,
    adjust_saturation,
    auto_white_balance,
    upscale,
)


def test_adjust_brightness_contrast():
    dummy = np.zeros((10, 10, 3), dtype=np.uint8) + 100
    res = adjust_brightness_contrast(dummy, brightness=10, contrast=1.2)
    assert res.shape == (10, 10, 3)
    assert res[0, 0, 0] == 130  # 100 * 1.2 + 10

    with pytest.raises(ValueError):
        adjust_brightness_contrast(np.array([]))

    with pytest.raises(ValueError):
        adjust_brightness_contrast(dummy, contrast=-0.5)


def test_sharpen():
    dummy = np.ones((20, 20, 3), dtype=np.uint8) * 128
    res = sharpen(dummy, factor=0.5)
    assert res.shape == (20, 20, 3)

    # 0 factor should return a copy unchanged
    res_zero = sharpen(dummy, factor=0.0)
    assert np.array_equal(dummy, res_zero)

    with pytest.raises(ValueError):
        sharpen(None)


def test_denoise():
    dummy = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
    res = denoise(dummy, d=3)
    assert res.shape == (20, 20, 3)

    res_zero = denoise(dummy, d=0)
    assert np.array_equal(dummy, res_zero)

    with pytest.raises(ValueError):
        denoise(np.array([]))


def test_adjust_saturation():
    dummy = np.zeros((10, 10, 3), dtype=np.uint8)
    dummy[:, :, 0] = 250  # Blue channel
    res = adjust_saturation(dummy, saturation=1.5)
    assert res.shape == (10, 10, 3)

    res_one = adjust_saturation(dummy, saturation=1.0)
    assert np.array_equal(dummy, res_one)

    with pytest.raises(ValueError):
        adjust_saturation(dummy, saturation=-1.0)


def test_auto_white_balance():
    dummy = np.zeros((10, 10, 3), dtype=np.uint8)
    dummy[:, :, 0] = 50   # Blue
    dummy[:, :, 1] = 100  # Green
    dummy[:, :, 2] = 150  # Red

    res = auto_white_balance(dummy)
    assert res.shape == (10, 10, 3)
    # Means should become closely balanced
    mean_b = np.mean(res[:, :, 0])
    mean_g = np.mean(res[:, :, 1])
    mean_r = np.mean(res[:, :, 2])
    assert abs(mean_b - mean_g) <= 5
    assert abs(mean_g - mean_r) <= 5


def test_upscale():
    dummy = np.zeros((20, 30, 3), dtype=np.uint8)
    res = upscale(dummy, scale_factor=2.0, method="bicubic")
    assert res.shape == (40, 60, 3)

    res_same = upscale(dummy, scale_factor=1.0)
    assert np.array_equal(dummy, res_same)

    with pytest.raises(ValueError):
        upscale(dummy, scale_factor=-1.0)

    with pytest.raises(ValueError):
        upscale(dummy, scale_factor=2.0, method="invalid_method")
