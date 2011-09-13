#!/usr/bin/env python

from __future__ import with_statement
from fabric.api import *
from fabric.decorators import *
import logging

from fabric_deploy.options import fetch

@task(default=True)
@runs_once
def list_variables():
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

# vim:set ft=python :
