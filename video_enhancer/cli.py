"""
Command Line Interface for Video Enhancer.
"""

import argparse
import sys
import os

from video_enhancer.enhancer import VideoEnhancer
from video_enhancer.utils import get_video_info, PRESETS


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="video-enhancer",
        description="Enhance video quality with custom filters or preset configurations.",
    )

    parser.add_argument(
        "-i", "--input", required=True, help="Path to input video file."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to save enhanced output video."
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        help=f"Enhancement preset. Options: {', '.join(PRESETS.keys())}.",
    )
    parser.add_argument(
        "--brightness",
        type=float,
        default=None,
        help="Brightness adjustment factor (-100 to 100). Default: 0.0.",
    )
    parser.add_argument(
        "--contrast",
        type=float,
        default=None,
        help="Contrast multiplier (>0). Default: 1.0.",
    )
    parser.add_argument(
        "--sharpen",
        type=float,
        default=None,
        help="Sharpening factor (0.0 to 3.0). Default: 0.0.",
    )
    parser.add_argument(
        "--denoise",
        action="store_true",
        default=None,
        help="Enable bilateral noise reduction filter.",
    )
    parser.add_argument(
        "--no-denoise",
        action="store_false",
        dest="denoise",
        help="Disable noise reduction filter.",
    )
    parser.add_argument(
        "--denoise-d",
        type=int,
        default=None,
        help="Pixel neighborhood diameter for denoising filter. Default: 5.",
    )
    parser.add_argument(
        "--saturation",
        type=float,
        default=None,
        help="Color saturation multiplier. Default: 1.0.",
    )
    parser.add_argument(
        "--auto-wb",
        action="store_true",
        default=None,
        help="Enable Gray World auto white balance.",
    )
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=None,
        help="Resolution scaling/upscaling factor (>0). Default: 1.0.",
    )
    parser.add_argument(
        "--upscale-method",
        choices=["bicubic", "lanczos", "linear", "nearest"],
        default=None,
        help="Interpolation method for resolution scaling. Default: bicubic.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Maximum number of frames to process.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print video metadata and exit.",
    )

    return parser.parse_args(args)


def main(args=None):
    parsed_args = parse_args(args)

    if not os.path.exists(parsed_args.input):
        print(f"Error: Input file '{parsed_args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if parsed_args.info:
        try:
            info = get_video_info(parsed_args.input)
            print("--- Video Information ---")
            print(f"File Path:   {info['file_path']}")
            print(f"Resolution:  {info['width']}x{info['height']}")
            print(f"FPS:         {info['fps']:.2f}")
            print(f"Frames:      {info['frame_count']}")
            print(f"Duration:    {info['duration_seconds']:.2f} seconds")
            return 0
        except Exception as e:
            print(f"Error reading video info: {e}", file=sys.stderr)
            sys.exit(1)

    if parsed_args.preset:
        enhancer = VideoEnhancer.from_preset(parsed_args.preset)
    else:
        enhancer = VideoEnhancer()

    # Apply parameter overrides from CLI
    if parsed_args.brightness is not None:
        enhancer.brightness = parsed_args.brightness
    if parsed_args.contrast is not None:
        enhancer.contrast = parsed_args.contrast
    if parsed_args.sharpen is not None:
        enhancer.sharpen_factor = parsed_args.sharpen
    if parsed_args.denoise is not None:
        enhancer.enable_denoise = parsed_args.denoise
    if parsed_args.denoise_d is not None:
        enhancer.denoise_d = parsed_args.denoise_d
    if parsed_args.saturation is not None:
        enhancer.saturation = parsed_args.saturation
    if parsed_args.auto_wb is not None:
        enhancer.enable_auto_wb = parsed_args.auto_wb
    if parsed_args.scale_factor is not None:
        enhancer.scale_factor = parsed_args.scale_factor
    if parsed_args.upscale_method is not None:
        enhancer.upscale_method = parsed_args.upscale_method

    print(f"Processing video: {parsed_args.input} -> {parsed_args.output}")

    def progress_callback(current, total):
        pct = (current / total * 100) if total > 0 else 0
        print(f"\rProgress: {current}/{total} frames ({pct:.1f}%)", end="", flush=True)

    try:
        results = enhancer.process_video(
            parsed_args.input,
            parsed_args.output,
            progress_callback=progress_callback,
            max_frames=parsed_args.max_frames,
        )
        print("\nEnhancement complete!")
        print(f"Output saved to: {results['output_path']}")
        print(f"Output Resolution: {results['output_resolution'][0]}x{results['output_resolution'][1]}")
        return 0
    except Exception as e:
        print(f"\nError processing video: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
