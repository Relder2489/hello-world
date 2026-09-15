import os
import tempfile
import pytest

from video_enhancer.cli import parse_args, main
from tests.test_enhancer import create_synthetic_video


def test_cli_parse_args():
    args = parse_args(["-i", "in.mp4", "-o", "out.mp4", "--preset", "vivid", "--brightness", "15"])
    assert args.input == "in.mp4"
    assert args.output == "out.mp4"
    assert args.preset == "vivid"
    assert args.brightness == 15.0


def test_cli_main_info(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "test_input.mp4")
        create_synthetic_video(input_file, width=32, height=24, fps=10.0, num_frames=3)

        ret = main(["-i", input_file, "-o", "dummy.mp4", "--info"])
        assert ret == 0

        captured = capsys.readouterr()
        assert "Video Information" in captured.out
        assert "32x24" in captured.out


def test_cli_main_process(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "test_input.mp4")
        output_file = os.path.join(tmpdir, "test_output.mp4")
        create_synthetic_video(input_file, width=32, height=24, fps=10.0, num_frames=3)

        ret = main(["-i", input_file, "-o", output_file, "--preset", "subtle", "--max-frames", "2"])
        assert ret == 0
        assert os.path.exists(output_file)

        captured = capsys.readouterr()
        assert "Enhancement complete!" in captured.out
