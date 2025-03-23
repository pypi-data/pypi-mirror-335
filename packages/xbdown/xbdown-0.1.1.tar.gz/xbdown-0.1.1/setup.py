# -*- coding: utf-8 -*-
from setuptools import setup
import os

setup(
    name="xbdown",
    version="0.1.1",
    py_modules=['xbdown'],
    install_requires=['libtorrent', 'requests', 'colorama'],
    entry_points={'console_scripts': ['xbdown = xbdown:main']},
    author="Python学霸",
    author_email="xueba@xb.com",
    description="强大的种子下载工具，优化性能与美观终端输出",
    long_description=open('README.md').read() if os.path.exists('README.md') else "",
    long_description_content_type="text/markdown",
    url="https://github.com/pythonxueba/xbdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)