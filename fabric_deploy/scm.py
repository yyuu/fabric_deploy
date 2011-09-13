#!/usr/bin/env python

from __future__ import with_statement
import sys
import os
from fabric.api import *
from fabric.decorators import *
from fabric.contrib import project

def fetch(key, default_val=None):
  import options
  return options.fetch(key, default_val)

class SCM(object):
  def head(self, *args, **kwargs):
    raise(NotImplementedError())

  def checkout(self, *args, **kwargs):
    raise(NotImplementedError())

  def repository_path(self, path="."):
    raise(NotImplementedError())

class Git(SCM):
  def head(self):
    return fetch('branch')

  def origin(self):
    return fetch('remote', 'origin')

  def checkout(self, revision, destination, perform_fetch=True):
    kwargs = {
      'git': fetch('git', 'git'),
      'remote': self.origin(),
      'repository': fetch('repository'),
      'destination': destination,
      'revision': revision,
    }

    execute = []
    execute.append('(test -d %(destination)s || %(git)s clone %(repository)s %(destination)s)' % kwargs)
    execute.append('cd %(destination)s' % kwargs)
    execute.append('%(git)s checkout -b deploy %(revision)s' % kwargs)
    if perform_fetch:
      execute.append('%(git)s fetch %(remote)s && %(git)s fetch --tags %(remote)s' % kwargs)
    execute.append('%(git)s reset --hard %(revision)s' % kwargs)
    if fetch('git_enable_submodules'):
      execute.append('%(git)s submodule init' % kwargs)
      execute.append('%(git)s submodule sync' % kwargs)
      execute.append('%(git)s submodule update --init --recursive' % kwargs)
    execute.append('%(git)s clean -d -x -f' % kwargs)
    return ' && '.join(execute)

  def __str__(self):
    return "git"

  def repository_path(self, path="."):
    realpath = os.path.realpath(path)
    repository = os.path.join(realpath, '.git')
    if os.path.isdir(repository):
      return realpath
    else:
      if realpath == os.path.sep:
        return None
      else:
        return self.repository_path(os.path.join(realpath, '..'))

class Subversion(SCM):
  def __str__(self):
    return "subversion"

  def repository_path(self, path="."):
    realpath = os.path.realpath(path)
    repository = os.path.join(realpath, '.svn')
    if os.path.isdir(repository):
      return self.repository_path(os.path.join(realpath, '..'))
    else:
      if realpath == os.path.sep:
        return None
      else:
        return realpath

class Mercurial(SCM):
  def __str__(self):
    return "mercurial"

  def repository_path(self, path):
    realpath = os.path.realpath(path)
    repository = os.path.join(realpath, '.hg')
    if os.path.isdir(repository):
      return realpath
    else:
      if realpath == os.path.sep:
        return None
      else:
        return self.repository_path(os.path.join(realpath, '..'))

# vim:set ft=python :
