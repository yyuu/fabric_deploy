#!/usr/bin/env python

import sys
import os
from fabric.api import *
from fabric.decorators import *
import logging
import time

import scm
import strategy

settings = {}

def fetch(key, default_val=None):
  val = settings.get(key)
  if hasattr(val, '__call__'): val = settings[key] = val()
  return default_val if val is None else val

def set(key, val=None):
  settings[key] = val

def cset(key, val=None):
  if fetch(key) is None: set(key, val)

cset('scm', 'git')
cset('application', 'app')
cset('repository', 'git@git:app.git')
cset('branch', 'master')
cset('remote', 'origin')
cset('git_enable_submodules', False)
cset('deploy_to', (lambda: '/u/apps/{name}'.format(name=fetch('application'))))
cset('shared_path', (lambda: '{dir}/shared'.format(dir=fetch('deploy_to'))))
cset('current_path', (lambda: '{dir}/current'.format(dir=fetch('deploy_to'))))
cset('releases_path', (lambda: '{dir}/releases'.format(dir=fetch('deploy_to'))))
cset('release_name', (lambda: time.strftime('%Y%m%d%H%M%S')))
cset('release_path', (lambda: '{dir}/{name}'.format(dir=fetch('releases_path'), name=fetch('release_name'))))
cset('latest_release', (lambda: fetch('release_path')))
cset('releases', (lambda: _get_releases()))
cset('previous_release', (lambda: _get_previous_release()))
cset('current_release', (lambda: _get_current_release()))
cset('keep_releases', 5)
cset('cached_path', (lambda: '{dir}/cached-copy'.format(dir=fetch('shared_path'))))

@task
@roles('app')
@runs_once
def _get_releases():
  releases = run('ls {releases_path}'.format(releases_path=fetch('releases_path'))).split()
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
}
cset('source', (lambda: source_table.get(fetch('scm'))()))
cset('revision', (lambda: fetch('source').head()))

cset('deploy_via', 'local_cache')
strategy_table = {
  'local_cache': strategy.LocalCacheStrategy,
}
cset('strategy', (lambda: strategy_table.get(fetch('deploy_via'))()))

cset('runner', 'app')

# vim:set ft=python :
