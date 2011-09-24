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

class Version(object):
  def __init__(self, filename='VERSION'):
    self.filename = filename
    self.major = self.minor = self.subminor = 0
    self.identifier = None
    self.modified = False
    self.update()

  def update(self):
    self.parse(self._read())

  def commit(self):
    saved = self.modified
    if self.modified:
      self._write(self.unparse(self.major, self.minor, self.subminor, self.identifier))
      local('git commit --all --message="version bumped to %s."' % (version))
    self.modified = False
    return saved

  def parse(self, s):
    parsed = s.split('.')
    self.major, _ = self._parse_entity(parsed[0])
    self.minor, _ = self._parse_entity(parsed[1])
    self.subminor, self.identifier = self._parse_entity(parsed[2])

  def _parse_entity(self, s):
    if s.isdigit():
      return (int(s), None)
    else:
      m = re.search('[0-9]+', s)
      if m is None:
        return (0, s)
      else:
        o = re.search('[^0-9]+', s)
        return (int(m.group()), o.group())

  def unparse(self, major=0, minor=0, subminor=0, identifier=None):
    s = '.'.join([ str(n) for n in [major, minor, subminor]])
    if identifier is not None:
      s += identifier
    return s

  def increase_major(self, identifier=None):
    if identifier == self.identifier:
      self.major += 1
      self.minor = 0
      self.subminor = 0
    else:
      if self.identifier is None:
        self.major += 1
        self.minor = 0
        self.subminor = 0
      self.identifier = identifier
      self.modified = True

  def increase_minor(self, identifier=None):
    if identifier == self.identifier:
      self.minor += 1
      self.subminor = 0
    else:
      if self.identifier is None:
        self.minor += 1
        self.subminor = 0
      self.identifier = identifier
      self.modified = True

  def increase_subminor(self, identifier=None):
    if identifier == self.identifier:
      self.subminor +=1
      self.modified = True
    else:
      if self.identifier is None:
        self.subminor +=1
      self.identifier = identifier
      self.modified = True

  def __str__(self):
    return self.unparse(self.major, self.minor, self.subminor, self.identifier)

  def _read(self):
    with contextlib.closing(open(self.filename)) as fp:
      return fp.read().strip()

  def _write(self, s):
    with contextlib.closing(open(self.filename, 'w')) as fp:
      fp.write(s + "\n")

version = Version()

@task
def bump(release=False):
  bump_subminor(release)

@task
def bump_subminor(release=False):
  identifier = 'git' if not release else None
  version.increase_subminor(identifier)
  version.commit()

@task
def bump_minor(release=False):
  identifier = 'git' if not release else None
  version.increase_minor(identifier)
  version.commit()

@task
def bump_major(release=False):
  identifier = 'git' if not release else None
  version.increase_major(identifier)
  version.commit()

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
  local('git tag release/%s' % (version))
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
  local('python setup.py build bdist bdist_egg sdist upload')

# vim:set ft=python :
