from setuptools import setup, find_packages

with open("album_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="album-metadata-editor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A professional tool for batch updating album metadata and artwork",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/album-metadata-editor",
    py_modules=["album_metadata_editor"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Editors",
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
    ],
    entry_points={
        "console_scripts": [
            "album-metadata=album_metadata_editor:main",
        ],
    },
)