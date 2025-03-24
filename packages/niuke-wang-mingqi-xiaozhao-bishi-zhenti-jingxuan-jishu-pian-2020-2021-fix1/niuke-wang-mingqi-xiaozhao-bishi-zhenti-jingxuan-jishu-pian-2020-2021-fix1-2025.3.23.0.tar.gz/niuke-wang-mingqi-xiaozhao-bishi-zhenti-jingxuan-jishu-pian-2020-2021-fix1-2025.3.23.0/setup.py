#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1
import os
from os import path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

for subdir, _, _ in os.walk('NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1'):
    fname = path.join(subdir, '__init__.py')
    open(fname, 'a').close()
    
setuptools.setup(
    name="niuke-wang-mingqi-xiaozhao-bishi-zhenti-jingxuan-jishu-pian-2020-2021-fix1",
    version=NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1.__version__,
    url="https://github.com/apachecn/niuke-wang-mingqi-xiaozhao-bishi-zhenti-jingxuan-jishu-pian-2020-2021-fix1",
    author=NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1.__author__,
    author_email=NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1.__email__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: Other/Proprietary License",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Documentation",
        "Topic :: Documentation",
    ],
    description="牛客网名企校招笔试真题精选技术篇 2020-2021",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[],
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            "niuke-wang-mingqi-xiaozhao-bishi-zhenti-jingxuan-jishu-pian-2020-2021-fix1=NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1.__main__:main",
            "NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1=NiukeWangMingqiXiaozhaoBishiZhentiJingxuanJishuPian20202021Fix1.__main__:main",
        ],
    },
    packages=setuptools.find_packages(),
    package_data={'': ['*']},
)
