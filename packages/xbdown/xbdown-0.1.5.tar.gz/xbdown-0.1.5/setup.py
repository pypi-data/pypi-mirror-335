# -*- coding: utf-8 -*-
from setuptools import setup
import os

# 项目根目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 读取 README.md 文件内容
def read_file(filename):
    """读取指定文件内容，若文件不存在返回空字符串"""
    filepath = os.path.join(BASE_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

setup(
    name="xbdown",
    version="0.1.5",
    py_modules=['xbdown'], 
    install_requires=[
        'libtorrent>=2.0.5', 
        'requests>=2.25.0',
        'colorama>=0.4.4',
    ],
    entry_points={
        'console_scripts': [
            'xbdown = xbdown:main', 
        ],
    },
    author="Python学霸",
    author_email="xueba@xb.com",
    description="强大的种子下载工具，优化性能与美观终端输出",
    long_description=read_file('README.md'),  
    long_description_content_type="text/markdown",
    url="https://github.com/pythonxueba/xbdown",
    license="MIT",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires='>=3.6',  
    keywords="torrent downloader magnet cli",  
)