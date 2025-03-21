#!/usr/bin/env python
from setuptools import setup, find_packages
import re


def get_version():
    init_py = open('amocrm/__init__.py').read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']

version = get_version()


setup(
    name='amocrm_api_async',
    version=version,
    packages=find_packages(),
    url='https://github.com/DoritosChips/amocrm_api_async',
    license='MIT license',
    author='Nikita Zolotov',
    author_email='nick.zolotov@gmail.com',
    description='Python API for Amocrm but async',
    long_description=open('README.rst').read(),
    install_requires=[
        'aiohttp',
        'pyjwt',
    ],
    extras_require={
        'cli': ['python-slugify', ],
    },
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'pyamogen=amocrm.v2.cli:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
