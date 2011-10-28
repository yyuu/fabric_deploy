#!/usr/bin/env python

from __future__ import with_statement
import sys
import os
from fabric.api import *
from fabric.decorators import *
from fabric.colors import *
import fabric.state
import logging
import StringIO

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

def command(name):
  if name.find('.') < 0:
    name = "%s.%s" % (os.path.splitext(os.path.basename(__file__))[0], name)
  commands = fabric.state.commands
  for key in name.split('.'):
    commands = commands.get(key)
  return commands

def invoke(name):
  return command(name)()

@task
@roles('app', 'web')
def setup():
  with settings(warn_only=True):
    dirs = [fetch('deploy_to'), fetch('releases_path'), fetch('shared_path')]
    dirs += map(lambda path: os.path.join(fetch('shared_path'), path), ['log', 'pids', 'system'])
    result = run('mkdir -p %(dirs)s && chmod g+w %(dirs)s' % dict(dirs=' '.join(dirs)))
    if result.failed:
      error('failed to setup.')

  if fetch('virtualenv') is not None:
    invoke('setup_virtualenv')

@task
@roles('app', 'web')
def setup_virtualenv():
  invoke('setup_pybundle')
  with settings(warn_only=True):
    result = run("""
      if ! test -d %(virtualenv)s; then
        virtualenv %(virtualenv)s || (rm -rf %(virtualenv)s; false);
      fi
    """ % var('virtualenv'))
    if result.failed:
      error('failed to create virtualenv.')

    invoke('upload_pybundle')

    result = run("""
      test -d %(virtualenv)s/build && rm -rf %(virtualenv)s/build; true
    """ % var('virtualenv', 'pybundle_path'))
    if result.failed:
      error('failed to cleanup old bulid.')

    result = run("""
      . %(virtualenv)s/bin/activate && easy_install pip && pip install --upgrade %(pybundle_path)s
    """ % var('virtualenv', 'pybundle_path'))
    if result.failed:
      error('failed to install pybundle.')

@task
@roles('app', 'web')
@runs_once
def setup_pybundle():
  with settings(warn_only=True):
    requirement = 'packages.txt'
    result = local("""
      if test -f %(requirement)s; then pip install --upgrade --requirement=%(requirement)s; else pip freeze --local > %(requirement)s; fi &&
      if test \! -f %(application)s.pybundle -o %(application)s.pybundle -ot %(requirement)s; then
        pip bundle --requirement=%(requirement)s %(application)s.pybundle;
      fi
    """ % var('application', requirement=requirement))
    if result.failed:
      error('failed to create pybundle.')

@task
@roles('app', 'web')
def upload_pybundle():
  with settings(warn_only=True):
    result = put('%(application)s.pybundle' % var('application'), fetch('pybundle_path'))
    if result.failed:
      error('failed to upload pybundle.')

@task(default=True)
@roles('app', 'web')
def default():
  invoke('update')
  invoke('restart')
  invoke('cleanup')

@task
@roles('app', 'web')
def update():
  invoke('update_code')
  invoke('symlink')

@task
@roles('app', 'web')
def update_code():
  try:
    fetch('strategy').deploy()
  except Exception, e:
    run('rm -rf %(latest_release)s; true' % var('latest_release'))
    error('failed to update code. (%(reason)s)' % dict(reason=str(e)))

  invoke('finalize_update')

@task
@roles('app', 'web')
def finalize_update():
  with settings(warn_only=True):
    result = run("""
      rm -rf %(latest_release)s/log %(latest_release)s/public/system %(latest_release)s/tmp/pids &&
      mkdir -p %(latest_release)s/public &&
      mkdir -p %(latest_release)s/tmp &&
      ln -s %(shared_path)s/log %(latest_release)s/log &&
      ln -s %(shared_path)s/system %(latest_release)s/public/system &&
      ln -s %(shared_path)s/pids %(latest_release)s/tmp/pids
    """ % var('latest_release', 'shared_path'))
    if result.failed:
      alert('failed to finalize update. try to delete temporal files.')
      run('rm -rf %(latest_release)s; true' % var('latest_release'))
      error('failed to finalize update.')

    if fetch('group_writable'):
      run('chmod -R g+w %(latest_release)s' % var('latest_release'))

@task
@roles('app', 'web')
def symlink():
  with settings(warn_only=True):
    result = run('rm -f %(current_path)s && ln -s %(latest_release)s %(current_path)s' % var('current_path', 'latest_release'))
    if result.failed:
      alert('failed to update symlink. try to rollback.')
      invoke('rollback')

@task
@roles('app')
def start():
  sudo('service %(service_name)s start' % var('service_name'))

@task
@roles('app')
def stop():
  sudo('service %(service_name)s stop' % var('service_name'))

@task
@roles('app')
def restart():
  sudo('service %(service_name)s restart || service %(service_name)s start' % var('service_name'))

@task
@roles('app')
def status():
  sudo('service %(service_name)s status' % var('service_name'))

@task
@roles('app', 'web')
def rollback():
  previous_release = fetch('previous_release')
  if previous_release is None:
    error('no previous releases.')
  run("""
    rm -f %(current_path)s && ln -s %(previous_release)s %(current_path)s
  """ % var('current_path', 'previous_release', 'latest_release'))
  run("""
    if [ `readlink %(current_path)s` != %(current_release)s ]; then rm -rf %(current_release)s; fi
  """ % var('current_path', 'current_release'))

@task
@roles('app', 'web')
def cleanup():
  releases = fetch('releases')
  keep_releases = int(fetch('keep_releases'))
  releases_path = fetch('releases_path')
  if keep_releases < len(releases):
    delete_releases = map(lambda release: os.path.join(releases_path, release), releases[0:-keep_releases])
    run('rm -rf %(delete_releases)s' % dict(delete_releases=' '.join(delete_releases)))

@task
@roles('web')
def disable(**kwargs):
  with settings(warn_only=True):
    reason = kwargs.get('reason', 'maintenance')
    until = kwargs.get('until', 'unknown')
    body = '<html><body>%(reason)s until %(until)s</body></html>' % dict(reason=reason, until=until)
    result = put(StringIO.StringIO(body), '%(shared_path)s/system/%(maintenance_basename)s.html' % var('shared_path', 'maintenance_basename'))
    if result.failed:
      invoke('enable')

@task
@roles('web')
def enable():
  run("""
    rm -f %(shared_path)s/system/%(maintenance_basename)s.html
  """ % var('shared_path', 'maintenance_basename'))

# vim:set ft=python :
