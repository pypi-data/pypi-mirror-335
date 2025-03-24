#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1
import os
from os import path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

for subdir, _, _ in os.walk('NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1'):
    fname = path.join(subdir, '__init__.py')
    open(fname, 'a').close()
    
setuptools.setup(
    name="nosql-shujuku-rumenjiaocheng-c-yuyan-biancheng-wang-fix1",
    version=NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1.__version__,
    url="https://github.com/apachecn/nosql-shujuku-rumenjiaocheng-c-yuyan-biancheng-wang-fix1",
    author=NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1.__author__,
    author_email=NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1.__email__,
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
    description="NoSQL数据库入门教程（C语言编程网）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[],
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            "nosql-shujuku-rumenjiaocheng-c-yuyan-biancheng-wang-fix1=NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1.__main__:main",
            "NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1=NosqlShujukuRumenjiaochengCYuyanBianchengWangFix1.__main__:main",
        ],
    },
    packages=setuptools.find_packages(),
    package_data={'': ['*']},
)
