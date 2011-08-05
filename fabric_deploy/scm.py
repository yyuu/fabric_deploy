#!/usr/bin/env python

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
    execute.append('(test -d {destination} || {git} clone {repository} {destination})'.format(**kwargs))
    execute.append('cd {destination}'.format(**kwargs))
    execute.append('{git} checkout -b deploy {revision}'.format(**kwargs))
    if perform_fetch:
      execute.append('{git} fetch {remote} && {git} fetch --tags {remote}'.format(**kwargs))
    execute.append('{git} reset --hard {revision}'.format(**kwargs))
    if fetch('git_enable_submodules'):
      execute.append('{git} submodule init'.format(**kwargs))
      execute.append('{git} submodule sync'.format(**kwargs))
      execute.append('{git} submodule update --init --recursive'.format(**kwargs))
    execute.append('{git} clean -d -x -f'.format(**kwargs))
    return ' && '.join(execute)

class Subversion(SCM):
  pass

class Mercurial(SCM):
  pass

# vim:set ft=python :
