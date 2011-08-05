#!/usr/bin/env python

try:
  from setuptools import setup, find_packages
except ImportError:
  from ez_setup import use_setuptools
  use_setuptools()
  from setuptools import setup, find_packages

setup(
  name='fabric_deploy',
  version='0.0.1',
  author='Yamashita Yuu',
  author_email='yamashita@geishatokyo.com',
  description='capistrano like deploy recipe for Fabric',
  license='BSD',
  keywords='fabric deploy',
  url='https://github.com/yyuu/fabric_deploy',
  long_description="""Capistrano like deploy recipe for Fabric.""",
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Topic :: Software Development',
    'Topic :: Software Development :: Build Tools',
    'Topic :: System :: Software Distribution',
    'Topic :: System :: Systems Administration',
    'License :: OSI Approved :: BSD License',
  ],
  platforms=[
    'POSIX'
  ],
  install_requires=[
    'Fabric',
  ],
  packages=find_packages(),
)
