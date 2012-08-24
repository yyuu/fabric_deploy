# fabric_deploy

## Overview

Capistrano like deploy recipe for Fabric.


## Requirements

* Fabric


## Usage

This recipe is just a template for basic deploy procedures.
You may need to override your own tasks in your fabfile.py.

Initialize directory structure for "development" stage.

    % fab development deploy.setup

Deploy application to "development" stage.

    % fab development deploy

Rollback to previously deployed application.

    % fab development deploy.rollback

Clean up old applications.

    % fab development deploy.cleanup


## Privilege configurations

This recipe assumes that you can ssh by user named "deploy" and "app" by default.

* deploy (user)
  * Used for application deployment.
  * Belongs same group as app.
  * sudo(8) should be granted without password.
* app (runner)
  * Used for running applications
  * Belongs same group as deploy.
  * No sudo(8) required.

You can change these names by overriding "user" and "runner" options.


## Examples

Following is a sample tasks for multistage deployment ("development" and "production").
Uses "supervisord" for service management.  This exapmle consists from 2 files.

* `./fabfile/__init__.py` - Basic configuration for deployment
* `./fabfile/deploy.py` - Overridden tasks for your deployment

`./fabfile/__init__.py`

    from fabric.api import *
    from fabric_deploy import options
    import deploy
    
    options.set('scm', 'git')
    options.set('application', 'myapp')
    options.set('repository', 'git@githum.com:yyuu/myapp.git')
    options.set('supervisord_pid',
      (lambda: '%(dir)s/tmp/pids/supervisord.pid' % dict(dir=options.fetch('current_path'))))
    options.set('supervisord_conf',
      (lambda: '%(dir)s/supervisord.conf' % dict(dir=options.fetch('current_path'))))
    
    @task
    def development():
      options.set('current_stage', 'development')
      env.roledefs.update({'app': [ 'alpha' ] })
    
    @task
    def production():
      options.set('current_stage', 'production')
      env.roledefs.update({ 'app': [ 'zulu' ] })


`./fabfile/deploy.py`

    from fabric_deploy.deploy import *
    
    @task
    @roles('app')
    def restart():
      with cd(fetch('current_path')):
        result = sudo("""
          (test -f %(supervisord_pid)s && kill -HUP `cat %(supervisord_pid)s`) || %(virtualenv)s/bin/supervisord -c %(supervisord_conf)s
        """ % var('virtualenv', 'supervisord_pid', 'supervisord_conf'), user=fetch('runner'))


## Author

Yamashita, Yuu <yamashita@geishatokyo.com>
