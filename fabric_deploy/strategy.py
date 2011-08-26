#!/usr/bin/env python

import sys
import os
from fabric.api import *
from fabric.decorators import *
from fabric.contrib import project
from fabric.tasks import Task

def fetch(key, default_val=None):
  import options
  return options.fetch(key, default_val)

class Strategy(object):
  def deploy(self, *args, **kwargs):
    raise(NotImplementedError())

class LocalCacheStrategy(Strategy):
  def deploy(self):
    cached_path = fetch('cached_path')
    if cached_path is None:
      abort('cached_path is None')

## deploy sub tree of the repository if deploy_subdir was specified.
    deploy_subdir = fetch('deploy_subdir')
    if deploy_subdir is not None:
      while 0 < len(deploy_subdir) and deploy_subdir.startswith('/'):
        deploy_subdir = deploy_subdir[1:]
      cached_path = os.path.join(cached_path, deploy_subdir)

    source = fetch('source')
    revision = fetch('revision')
    project.rsync_project(local_dir='./', remote_dir=cached_path, delete=True)
    run(source.checkout(revision, cached_path, perform_fetch=False))

    latest_release = fetch('latest_release')
    run("""
      rsync -lrpt --chmod=Dgo+rx,F=r {cached_path}/* {latest_release} && (echo {revision} > {release_path}/REVISION)
    """.format(cached_path=cached_path,
               latest_release=latest_release,
               revision=revision,
               release_path=fetch('release_path')))

  def __str__(self):
    return "local_cache"

class RemoteCacheStrategy(Strategy):
  def deploy(self):
    cached_path = fetch('cached_path')
    if cached_path is None:
      abort('cached_path is None')

## deploy sub tree of the repository if deploy_subdir was specified.
    deploy_subdir = fetch('deploy_subdir')
    if deploy_subdir is not None:
      while 0 < len(deploy_subdir) and deploy_subdir.startswith('/'):
        deploy_subdir = deploy_subdir[1:]
      cached_path = os.path.join(cached_path, deploy_subdir)

    source = fetch('source')
    revision = fetch('revision')
    run(source.checkout(revision, cached_path))

    latest_release = fetch('latest_release')
    run("""
      rsync -lrpt --chmod=Dgo+rx,F=r {cached_path}/* {latest_release} && (echo {revision} > {release_path}/REVISION)
    """.format(cached_path=cached_path,
               latest_release=latest_release,
               revision=revision,
               release_path=fetch('release_path')))

  def __str__(self):
    return "remote_cache"

# vim:set ft=python :
