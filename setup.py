#!/usr/bin/env python
import codecs
import os.path
import re
import sys

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
]

setup_options = dict(
    name='lld',
    version=find_version("client", "__init__.py"),
    description='Command Line Environment for UAT',
    long_description=read('README.rst'),
    author='ZHAO YU',
    scripts=['client/cli.py'],
    packages=find_packages(),
    package_data={'client': []},
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'lld = client.cli:main',
        ],
    },
)

setup(**setup_options)
