#!/usr/bin/env python

import sys
import os
from fabric.api import *
from fabric.decorators import *
from fabric.colors import *
import logging

import options
from options import fetch

def var(*keys, **kwargs):
  for key in keys:
    kwargs[key] = fetch(key)
  return kwargs

def notice(*args):
  logging.info(green(*args))

def alert(*args):
  logging.warn(yellow(*args))

def error(*args):
  logging.error(red(*args))
  abort(red(*args))

@task
@roles('app')
def setup():
  with settings(warn_only=True):
    dirs = [fetch('deploy_to'), fetch('releases_path'), fetch('shared_path')]
    dirs += map(lambda path: os.path.join(fetch('shared_path'), path), ['log', 'pids', 'system'])
    result = run('mkdir -p {dirs} && chmod g+w {dirs}'.format(dirs=' '.join(dirs)))
    if result.failed:
      error('failed to setup.')

  if fetch('virtualenv') is not None:
    setup_virtualenv()

@task
@roles('app')
def setup_virtualenv():
  setup_pybundle()
  with settings(warn_only=True):
    result = run("""
      if ! test -d {virtualenv}; then
        virtualenv {virtualenv} || (rm -rf {virtualenv}; false);
      fi
    """.format(**var('virtualenv')))
    if result.failed:
      error('failed to create virtualenv.')

    result = run("""
      . {virtualenv}/bin/activate && pip install {pybundle_path}
    """.format(**var('virtualenv', 'pybundle_path')))
    if result.failed:
      error('failed to install pybundle.')

@task
@roles('app')
@runs_once
def setup_pybundle():
  with settings(warn_only=True):
    requirement = 'packages.txt'
    result = local("""
      if ! test -f {application}.pybundle; then
        ( test -f {requirement} || pip freeze --local > {requirement} ) && pip bundle --requirement={requirement} {application}.pybundle;
      fi
    """.format(**var('application', requirement=requirement)))
    if result.failed:
      error('failed to create pybundle.')

    result = put('{application}.pybundle'.format(**var('application')), fetch('pybundle_path'))
    if result.failed:
      error('failed to upload pybundle.')

@task(default=True)
@roles('app')
def default():
  update()
  restart()

@task
@roles('app')
def update():
  update_code()
  symlink()

@task
@roles('app')
def update_code():
  try:
    fetch('strategy').deploy()
  except Exception, error:
    run('rm -rf {latest_release}; true'.format(**var('latest_release')))
    error('failed to update code.')

  finalize_update()

@task
@roles('app')
def finalize_update():
  with settings(warn_only=True):
    result = run("""
      rm -rf {latest_release}/log {latest_release}/public/system {latest_release}/tmp/pids &&
      mkdir -p {latest_release}/public &&
      mkdir -p {latest_release}/tmp &&
      ln -s {shared_path}/log {latest_release}/log &&
      ln -s {shared_path}/system {latest_release}/public/system &&
      ln -s {shared_path}/pids {latest_release}/tmp/pids
    """.format(**var('latest_release', 'shared_path')))
    if result.failed:
      alert('failed to finalize update. try to delete temporal files.')
      run('rm -rf {latest_release}; true'.format(**var('latest_release')))
      error('failed to finalize update.')

    if fetch('group_writable'):
      run('chmod -R g+w {latest_release}'.format(**var('latest_release')))

@task
@roles('app')
def symlink():
  with settings(warn_only=True):
    result = run('rm -f {current_path} && ln -s {latest_release} {current_path}'.format(**var('current_path', 'latest_release')))
    if result.failed:
      alert('failed to update symlink. try to rollback.')
      rollback()

@task
@roles('app')
def start():
  sudo('service {service_name} start'.format(**var('service_name')))

@task
@roles('app')
def stop():
  sudo('service {service_name} stop'.format(**var('service_name')))

@task
@roles('app')
def restart():
  sudo('service {service_name} restart || service {service_name} start'.format(**var('service_name')))

@task
@roles('app')
def status():
  sudo('service {service_name} status'.format(**var('service_name')))

@task
@roles('app')
def rollback():
  previous_release = fetch('previous_release')
  if previous_release is None:
    error('no previous releases.')
  run("""
    rm -f {current_path} && ln -s {previous_release} {current_path}
  """.format(**var('current_path', 'previous_release', 'latest_release')))
  run("""
    if [ `readlink {current_path}` != {current_release} ]; then rm -rf {current_release}; fi
  """.format(**var('current_path', 'current_release')))

@task
@roles('app')
def cleanup():
  releases = fetch('releases')
  keep_releases = int(fetch('keep_releases'))
  releases_path = fetch('releases_path')
  if keep_releases < len(releases):
    delete_releases = map(lambda release: os.path.join(releases_path, release), releases[0:-keep_releases])
    run('rm -rf {delete_releases}'.format(delete_releases=' '.join(delete_releases)))

# vim:set ft=python :
