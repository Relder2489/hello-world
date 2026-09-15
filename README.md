# Video Enhancer

A flexible Python library and CLI tool for enhancing video quality. It provides frame-by-frame image enhancement filters including brightness/contrast adjustments, unsharp sharpening, bilateral denoising, saturation boost, auto white balancing, and resolution upscaling.

---

## Features

- **Brightness & Contrast Adjustment**: Fine-tune contrast multiplier and brightness levels.
- **Unsharp Mask Sharpening**: Increase image clarity and edge detail.
- **Bilateral Denoising**: Filter out video noise while preserving crisp edges.
- **Color Saturation**: Adjust color saturation dynamically.
- **Auto White Balance**: Gray World algorithm to normalise color channels.
- **Resolution Upscaling**: Upscale videos using bicubic, Lanczos, linear, or nearest neighbor interpolation algorithms.
- **Built-in Presets**: Quick options including `subtle`, `balanced`, `vivid`, and `hd_upscale`.
- **CLI & Python API**: Full support for both terminal workflow and custom Python scripts.

---

## Installation

```bash
pip install -e .
```

Dependencies:
- Python >= 3.8
- `opencv-python-headless`
- `numpy`
- `Pillow`

---

## Command Line Usage

### 1. View Video Information
```bash
video-enhancer -i input.mp4 -o output.mp4 --info
```

### 2. Enhance Using a Preset
```bash
video-enhancer -i input.mp4 -o output.mp4 --preset vivid
```

Available presets:
- `subtle`: Mild contrast and slight sharpening.
- `balanced`: Brightness/contrast boost, moderate sharpening, and bilateral denoising.
- `vivid`: High contrast, saturation boost, sharpening, denoising, and auto white balance.
- `hd_upscale`: Balanced enhancement plus 2x bicubic resolution upscaling.

### 3. Custom Enhancement Options
```bash
video-enhancer -i input.mp4 -o output.mp4 \
  --brightness 10 \
  --contrast 1.2 \
  --sharpen 0.6 \
  --denoise \
  --saturation 1.15 \
  --scale-factor 1.5 \
  --upscale-method bicubic
```

---

## Python API Usage

```python
from video_enhancer import VideoEnhancer

# Initialize enhancer with custom settings or preset
enhancer = VideoEnhancer.from_preset("balanced", scale_factor=2.0)

# Process video file
results = enhancer.process_video(
    input_path="input.mp4",
    output_path="output_enhanced.mp4",
    progress_callback=lambda current, total: print(f"{current}/{total} frames")
)

print("Output resolution:", results["output_resolution"])
```

---

## Testing

Run unit test suite with `pytest`:

```bash
pytest -v
```
