#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import ShenghuaGuancaiQuantuiWenji2020112Fix1
import os
from os import path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

for subdir, _, _ in os.walk('ShenghuaGuancaiQuantuiWenji2020112Fix1'):
    fname = path.join(subdir, '__init__.py')
    open(fname, 'a').close()
    
setuptools.setup(
    name="shenghua-guancai-quantui-wenji-2020-11-2-fix1",
    version=ShenghuaGuancaiQuantuiWenji2020112Fix1.__version__,
    url="https://github.com/apachecn/shenghua-guancai-quantui-wenji-2020-11-2-fix1",
    author=ShenghuaGuancaiQuantuiWenji2020112Fix1.__author__,
    author_email=ShenghuaGuancaiQuantuiWenji2020112Fix1.__email__,
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
    description="生化棺材劝退文集 2020.11.2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[],
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            "shenghua-guancai-quantui-wenji-2020-11-2-fix1=ShenghuaGuancaiQuantuiWenji2020112Fix1.__main__:main",
            "ShenghuaGuancaiQuantuiWenji2020112Fix1=ShenghuaGuancaiQuantuiWenji2020112Fix1.__main__:main",
        ],
    },
    packages=setuptools.find_packages(),
    package_data={'': ['*']},
)
