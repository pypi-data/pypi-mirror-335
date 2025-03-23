# Building setup to package 'emp_utl'
import os
from setuptools import setup, find_packages

# Reading README.md as description
with open(file='src/README.md', mode='r', encoding='utf-8') as fh:
    long_description = fh.read()

# Reading requirements.txt for all modules
with open(file='src/requirements.txt', mode='r', encoding='utf-8') as f:
    required = f.read().splitlines()

# Setup - 'emp_utl' module
setup(
    name = 'emp_utl',
    version = '1.1.0',
    description = "Customized modules for reusability in Project Enterprise Management Program (EMP)",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'AbdoCherry',
    packages = find_packages(where = 'src', include = ['emp_utl*']),
    package_dir = {'': 'src'},
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires = required,
    license = 'MIT',
    url = 'https://github.com/AbdoCherry/EMP_UTL-S',
    python_requires = '>=3.8',
)