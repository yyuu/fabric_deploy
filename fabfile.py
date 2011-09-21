#!/usr/bin/env python

from __future__ import with_statement
import contextlib
from fabric.api import *
from fabric.decorators import *
from fabric_deploy.options import fetch
import logging
import re

@task(default=True)
@runs_once
def list():
## TODO: generate non-lazy keys automaticaly. see full keys from ./fabric_deploy/options.py.
  immediate_keys = [
    "application",
    "branch",
    "cached_path",
    "current_path",
    "deploy_subdir",
    "deploy_to",
    "deploy_via",
    "git_enable_submodules",
    "group_writable",
    "latest_release",
    "pybundle_path",
    "release_name",
    "release_path",
    "releases_path",
    "remote",
    "repository",
    "revision",
    "runner",
    "scm",
    "service_name",
    "shared_path",
    "source",
    "strategy",
    "user",
    "virtualenv",
  ]

  for key in immediate_keys:
    print("%(key)s = %(val)s" % dict(key=key, val=fetch(key)))

def parse_version(s):
  parsed = []
  for n in s.strip().split('.'):
    if not n.isdigit():
      m = re.match('[0-9]+', n)
      n = m.group() if m is not None else 0
    parsed.append(int(n))
  return parsed

def read_version():
  with contextlib.closing(open('VERSION')) as fp:
    return fp.read()

def write_version(s):
  with contextlib.closing(open('VERSION', 'w')) as fp:
    fp.write(s)

def get_version_info():
  return parse_version(read_version())

def put_version_info(version_info, release=False):
  version = ".".join([ str(n) for n in version_info ])
  if not release:
    version += 'git'
  write_version(version)
  local('git commit --all --message="version bumped to %s."' % (version))

@task
def bump(release=False):
  version_info = get_version_info()
  target = 2
  version_info[target] += 1
  for i in xrange(target+1, len(version_info)):
    version_info[i] = 0
  put_version_info(version_info, release)

@task
def bump_minor(release=False):
  version_info = get_version_info()
  target = 1
  version_info[target] += 1
  for i in xrange(target+1, len(version_info)):
    version_info[i] = 0
  put_version_info(version_info, release)

@task
def bump_major(release=False):
  version_info = get_version_info()
  target = 0
  version_info[target] += 1
  for i in xrange(target+1, len(version_info)):
    version_info[i] = 0
  put_version_info(version_info, release)

def try_release(major=False, minor=False, release=False):
  clean()
  test()
  package()
  if major:
    bump_major(release=release)
  elif minor:
    bump_minor(release=release)
  else:
    bump(release=release)

@task
def release(major=False, minor=False):
  try_release(major=major, minor=minor, release=True)
  local('git tag release/%s' % (read_version()))
  upload()
  bump(release=False)

@task
def snapshot(major=False, minor=False):
  try_release(major=major, minor=minor, release=False)

@task
def clean():
  local('python setup.py clean')

@task
def test():
  local('python setup.py test')

@task
def package():
  local('python setup.py build bdist bdist_egg sdist')

@task
def upload():
  clean()
  test()
  package()
  local('python setup.py upload')

# vim:set ft=python :
