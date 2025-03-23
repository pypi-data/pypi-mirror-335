#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import RiscvSpecV21ZhongwenbanFix1
import os
from os import path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

for subdir, _, _ in os.walk('RiscvSpecV21ZhongwenbanFix1'):
    fname = path.join(subdir, '__init__.py')
    open(fname, 'a').close()
    
setuptools.setup(
    name="riscv-spec-v2-1-zhongwenban-fix1",
    version=RiscvSpecV21ZhongwenbanFix1.__version__,
    url="https://github.com/apachecn/riscv-spec-v2-1-zhongwenban-fix1",
    author=RiscvSpecV21ZhongwenbanFix1.__author__,
    author_email=RiscvSpecV21ZhongwenbanFix1.__email__,
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
    description="riscv spec v2.1 中文版",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[],
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            "riscv-spec-v2-1-zhongwenban-fix1=RiscvSpecV21ZhongwenbanFix1.__main__:main",
            "RiscvSpecV21ZhongwenbanFix1=RiscvSpecV21ZhongwenbanFix1.__main__:main",
        ],
    },
    packages=setuptools.find_packages(),
    package_data={'': ['*']},
)
