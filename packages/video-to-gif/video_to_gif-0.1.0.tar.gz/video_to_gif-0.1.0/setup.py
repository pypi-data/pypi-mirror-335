from setuptools import setup, find_packages

setup(
    name="video_to_gif",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["moviepy"],
    entry_points={
        "console_scripts": ["gif-convert=gif_converter:main"]
    },
    author="Your Name",
    author_email="your_email@example.com",
    description="A simple tool to convert videos to GIFs",
    url="https://github.com/yourusername/video-to-gif",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
