from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flac-to-mp3-converter",
    version="1.0.0",
    author="MACHINO11",
    author_email="machino11.m11@gmail.com",
    description="A professional tool for converting FLAC files to MP3 with metadata preservation",
    long_description= long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Iammachino11/python-sandbox/audio-stuff/flac-to-mp3-converter",
    py_modules=["flac_to_mp3_converter"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mutagen>=1.47.0",
        "pydub>=0.25.1",
    ],
    entry_points={
        "console_scripts": [
            "flac-to-mp3=flac_to_mp3_converter:main",
        ],
    },
)