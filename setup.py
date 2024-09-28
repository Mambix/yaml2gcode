# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

here = os.path.abspath(os.path.dirname(__file__))

NAME = 'yaml2gcode'
about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)

setup(
    name=NAME,
    version=about['__version__'],
    description="Easily automate generating GCODE from yaml definitions/macros",
    license="MIT",
    author="Mambix Ltd.",
    author_email="ledi.mambix@gmail.com",
    url="https://github.com/Mambix/yaml2gcode",
    packages=find_packages(exclude=('tests')),
    scripts=['bin/yaml2gcode'],
    entry_points={'console_scripts': ['yaml2gcode=yaml2gcode:main']},
    install_requires=['PyYaml'],
    long_description=long_description,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
    ]
)
