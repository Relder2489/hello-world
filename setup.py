from setuptools import setup, find_packages

setup(
    name="video-enhancer",
    version="0.1.0",
    description="Python toolkit and CLI to enhance video quality (brightness, contrast, sharpen, denoise, saturation, upscaling).",
    author="Jules",
    packages=find_packages(),
    install_requires=[
        "opencv-python-headless>=4.5.0",
        "numpy>=1.20.0",
        "Pillow>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "video-enhancer=video_enhancer.cli:main",
        ],
    },
    python_requires=">=3.8",
)
