#!/usr/bin/env python
import codecs
import os.path
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    'click==8.0.3',
    'requests==2.26.0',
    'sseclient==0.0.27',
    'prettytable==2.2.1',
]

setup_options = dict(
    name='box',
    python_requires='>3.8.0',
    version=find_version("cli", "__init__.py"),
    description='Command Line Environment for UAT',
    long_description=read('README.rst'),
    author='ZHAO YU',
    scripts=['cli/box.py', 'cli/uat.py'],
    packages=find_packages(include=['cli']),
    install_requires=install_requires,
    dependency_links=[
        'http://mirrors.idiaoyan.cn/repository/pypi/',
    ],
    entry_points={
        'console_scripts': [
            'box = cli.box:main',
            'uat = cli.uat:main',
        ],
    },
)

setup(**setup_options)
