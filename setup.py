#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name="thumbor_icc",
    packages=find_packages(),
    version="0.1.1",
    description="Color management filters for thumbor",
    author="Lorenz Schori",
    author_email="lo@znerol.ch",
    keywords=["thumbor", "icc", "images"],
    license="MIT",
    url="https://github.com/znerol/thumbor-icc",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Graphics :: Presentation"
    ],
    install_requires=[
        "thumbor<7.0.0",
        "Pillow"
    ],
    long_description="""\
Thumbor is a smart imaging service. It enables on-demand crop, resizing and
flipping of images. This module provide support for color management profiles.
"""
)
