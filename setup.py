#!/usr/bin/env python

try:
  from setuptools import setup, find_packages
except ImportError:
  from ez_setup import use_setuptools
  use_setuptools()
  from setuptools import setup, find_packages

setup(
  name='fabric_deploy',
  version='0.2.1git',
  description='capistrano like deploy recipe for fabric',
  author='Yamashita Yuu',
  author_email='yamashita@geishatokyo.com',
  url='http://www.geishatokyo.com/',
  install_requires=[
    'Fabric>=1.2',
  ],
  packages=find_packages(),
)
