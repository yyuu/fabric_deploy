# fabric_deploy

## Overview

Capistrano like deploy recipe for Fabric.


## Requirements

* Fabric


## Usage

this recipe is just a template for basic deploy procedures.
you may need to override your own tasks in your fabfile.py.

initialize directory structure for "development" stage.

    % fab development deploy.setup

deploy application to "development" stage.

    % fab development deploy

rollback to previously deployed application.

    % fab development deploy.rollback

clean up old applications.

    % fab development deploy.cleanup


## Examples

this is a sample tasks for multistage deployment ("development" and "production").
uses "supervisor" for service management.

following exapmle consists from 2 files of "./fabfile/\__init\__.py" and "./fabfile/deploy.py".

* "./fabfile/\__init\__.py"
** basic configuration for deployment
* "./fabfile/deploy.py"
** overridden tasks for your deployment

"./fabfile/\__init\__.py"

    from fabric.api import *
    from fabric_deploy import options
    import deploy
    
    options.set('scm', 'git')
    options.set('application', 'myapp')
    options.set('repository', 'git@githum.com:yyuu/myapp.git')
    options.set('service_name',
      (lambda: '%(app)s.%(env)s' % dict(app=options.fetch('application'), env=options.fetch('current_stage'))))
    options.set('virtualenv',
      (lambda: '%(dir)s/virtualenv' % dict(dir=fetch('shared_path'))))
    options.set('supervisord_pid',
      (lambda: '%(dir)s/tmp/pids/supervisord.pid' % dict(dir=options.fetch('current_path'))))
    options.set('supervisord_conf',
      (lambda: '%(dir)s/supervisord.conf' % dict(dir=options.fetch('current_path'))))
    options.set('pybundle_path',
      (lambda: '%(dir)s/system/myapp.pybundle' % dict(dir=fetch('shared_path'))))
    
    @task
    def development():
      options.set('current_stage', 'production')
      if options.fetch('user'): env.user = options.fetch('user')
      env.roledefs.update({'app': [ 'alpha' ] })
    
    @task
    def production():
      options.set('current_stage', 'production')
      if options.fetch('user'): env.user = options.fetch('user')
      env.roledefs.update({ 'app': [ 'zulu' ] })


"./fabfile/deploy.py"

    from fabric_deploy.deploy import *
    from fabric_deploy import deploy
    
    @task
    @roles('app')
    def restart():
      with cd(fetch('current_path')):
        result = sudo("""
          (test -f %(supervisord_pid)s && kill -HUP `cat %(supervisord_pid)s`) || %(virtualenv)s/bin/supervisord -c %(supervisord_conf)s
        """ % var('virtualenv', 'supervisord_pid', 'supervisord_conf'), user=fetch('runner'))
    deploy.restart = restart


## Author

Yamashita, Yuu <yamashita@geishatokyo.com>
