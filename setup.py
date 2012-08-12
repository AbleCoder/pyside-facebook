#! /usr/bin/env python
#
# This file is part of PySide-Facebook.
# Copyright (c) 2012 Brandon Orther. All rights reserved.
#
# The full license is available in the LICENSE file that was distributed with this source code.
#
# Author: Brandon Orther <an.able.coder@gmail.com>

from setuptools import setup, find_packages

setup(
    name = "pyside-facebook",
    description = "A general purpose PySide library to interact with facebook's API",
    long_description = open("README.md").read(),

    version = "0.0.0a1",

    author = "Brandon Orther",
    author_email = "an.able.coder@gmail.com",

    py_modules=[
        'pyside_facebook',
    ],

    license = "BSD",
    url = "https://github.com/AbleCoder/pyside-facebook"
)
