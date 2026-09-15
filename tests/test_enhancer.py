import os
import tempfile
import pytest
import numpy as np
import cv2

from video_enhancer.enhancer import VideoEnhancer
from video_enhancer.utils import get_video_info, PRESETS, select_fourcc_codec


def create_synthetic_video(file_path: str, width: int = 64, height: int = 48, fps: float = 10.0, num_frames: int = 5):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(file_path, fourcc, fps, (width, height))
    for i in range(num_frames):
        frame = np.full((height, width, 3), fill_value=i * 20, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_preset_instantiation():
    for preset_name in PRESETS:
        enhancer = VideoEnhancer.from_preset(preset_name)
        assert isinstance(enhancer, VideoEnhancer)

    with pytest.raises(ValueError):
        VideoEnhancer.from_preset("non_existent_preset")


def test_process_frame():
    enhancer = VideoEnhancer.from_preset("balanced", scale_factor=1.5)
    frame = np.ones((40, 40, 3), dtype=np.uint8) * 100
    out = enhancer.process_frame(frame)
    assert out.shape == (60, 60, 3)


def test_process_video_workflow():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "test_input.mp4")
        output_file = os.path.join(tmpdir, "test_output.mp4")

        create_synthetic_video(input_file, width=64, height=48, fps=10.0, num_frames=5)

        info = get_video_info(input_file)
        assert info["width"] == 64
        assert info["height"] == 48
        assert info["frame_count"] == 5

        enhancer = VideoEnhancer(
            brightness=10.0,
            contrast=1.2,
            sharpen_factor=0.5,
            enable_denoise=True,
            scale_factor=2.0,
        )

        progress_calls = []

        def callback(cur, tot):
            progress_calls.append((cur, tot))

        res = enhancer.process_video(input_file, output_file, progress_callback=callback)

        assert res["frames_processed"] == 5
        assert res["output_resolution"] == (128, 96)
        assert len(progress_calls) == 5
        assert os.path.exists(output_file)

        out_info = get_video_info(output_file)
        assert out_info["width"] == 128
        assert out_info["height"] == 96


def test_select_fourcc_codec():
    assert select_fourcc_codec("test.mp4") == cv2.VideoWriter_fourcc(*"mp4v")
    assert select_fourcc_codec("test.avi") == cv2.VideoWriter_fourcc(*"MJPG")
    assert select_fourcc_codec("test.mkv") == cv2.VideoWriter_fourcc(*"VP80")
