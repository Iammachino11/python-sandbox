from setuptools import setup, find_packages

with open("tree_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="directory-tree-generator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A professional tool for generating visual directory tree structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/directory-tree-generator",
    py_modules=["directory_tree_generator"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Documentation",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    entry_points={
        "console_scripts": [
            "tree-gen=directory_tree_generator:main",
            "dirtree=directory_tree_generator:main",
        ],
    },
)