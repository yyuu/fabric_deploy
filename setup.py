#!/usr/bin/env python

try:
  from setuptools import setup, find_packages
except ImportError:
  from ez_setup import use_setuptools
  use_setuptools()
  from setuptools import setup, find_packages

import contextlib
version = None
with contextlib.closing(open('VERSION')) as fp:
  version = fp.read().strip()

setup(
  name='fabric_deploy',
  version=version,
  description='capistrano like deploy recipe for fabric',
  author='Yamashita Yuu',
  author_email='yamashita@geishatokyo.com',
  url='https://github.com/yyuu/fabric_deploy',
  install_requires=[
    'Fabric>=1.2',
  ],
  packages=find_packages(),
)
