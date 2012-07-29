#!/usr/bin/env python

from __future__ import with_statement
import sys
import os
from fabric.api import *
from fabric.decorators import *
import logging
import time

import scm
import strategy

def fetch(key, default_val=None):
  val = env.get(key)
  if hasattr(val, '__call__'):
    val = val()
    set(key, val)
  return default_val if val is None else val

def set(key, val=None):
  env[key] = val

def cset(key, val=None):
  if fetch(key) is None: set(key, val)

## the type of your source code management system.
cset('scm', 'git')
## the name of your application.
cset('application', 'app')
## the url of your application.
cset('repository', 'git@git:app.git')
## the brach on scm to deploy.
cset('branch', 'master')
cset('remote', 'origin')
cset('git_enable_submodules', False)
## the base path of application deployment.
cset('deploy_to', (lambda: '/u/apps/%(name)s' % dict(name=fetch('application'))))
## the path to the shared resources of deployed application. (such like logs)
cset('shared_path', (lambda: '%(dir)s/shared' % dict(dir=fetch('deploy_to'))))
## the path to the currently deployed application. (symlink)
cset('current_path', (lambda: '%(dir)s/current' % dict(dir=fetch('deploy_to'))))
## the path to the directory where the all deployed applications are in.
cset('releases_path', (lambda: '%(dir)s/releases' % dict(dir=fetch('deploy_to'))))
## the unique name for new deployment.
cset('release_name', (lambda: time.strftime('%Y%m%d%H%M%S')))
## the path to the new deployment of the application.
cset('release_path', (lambda: '%(dir)s/%(name)s' % dict(dir=fetch('releases_path'), name=fetch('release_name'))))
## the path to the latest application.
cset('latest_release', (lambda: fetch('release_path')))
## the list of all deployed applications.
cset('releases', (lambda: _get_releases()))
## the path to the previously deployed application.
cset('previous_release', (lambda: _get_previous_release()))
cset('current_release', (lambda: _get_current_release()))
## how much number to keep deployed applications.
cset('keep_releases', 5)
cset('cached_path', (lambda: '%(dir)s/cached-copy' % dict(dir=fetch('shared_path'))))

@task
@roles('app')
@runs_once
def _get_releases():
  releases = run('ls %(releases_path)s' % dict(releases_path=fetch('releases_path'))).split()
  releases.sort()
  return releases

@task
@roles('app')
@runs_once
def _get_previous_release():
  releases = fetch('releases')
  releases_path = fetch('releases_path')
  if 0 < len(releases):
    return os.path.join(releases_path, releases[-2])

@task
@roles('app')
@runs_once
def _get_current_release():
  releases = fetch('releases')
  releases_path = fetch('releases_path')
  if 0 < len(releases):
    return os.path.join(releases_path, releases[-1])

source_table = {
  'git': scm.Git,
  'mercurial': scm.Mercurial,
}
cset('source', (lambda: source_table.get(fetch('scm'))()))
cset('revision', (lambda: fetch('source').head()))

## specify deployment strategy. only local_cache is available as of now.
cset('deploy_via', 'local_cache')
strategy_table = {
  'local_cache': strategy.LocalCacheStrategy,
}
cset('strategy', (lambda: strategy_table.get(fetch('deploy_via'))()))

## deployment user.
set('user', 'deploy')

## application runner user.
cset('runner', 'app')

## deploy sub tree of the repository if deploy_subdir was specified.
#cset('deploy_subdir', 'path/to/somewhere')

cset('virtualenv', (lambda: '%(dir)s/virtualenv' % dict(dir=fetch('shared_path'))))
cset('pybundle_path', (lambda: '/tmp/%(name)s.pybundle' % dict(name=fetch('application'))))
cset('service_name', (lambda: fetch('application')))

cset('maintenance_basename', 'maintenance')

# vim:set ft=python :
