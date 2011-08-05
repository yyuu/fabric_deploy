# fabric-deploy-recipe

## overview

capistrano like deploy recipe for Fabric.


## requirements

* Fabric


## usage

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


## examples

this is a sample tasks for multistage deployment ("development" and "production").
uses "supervisord" for service management.

following exapmle consists from 2 files of `"./fabfile/__init__.py" and "./fabfile/__init__.py".

* "./fabfile/__init__.py"
** basic configuration for deployment
* "./fabfile/deploy.py"
** overridden tasks for deployment

"./fabfile/__init__.py"

    from fabric.api import *
    from fabric_deploy import options
    import deploy
    
    options.set('scm', 'git')
    options.set('application', 'konjak')
    options.set('repository', 'ssh://git@git.geishatokyo.com:10022/srv/repos/git/yyuu/konjak.git')
    options.set('service_name', (lambda: '{app}.{env}'.format(app=options.fetch('application'), env=options.fetch('current_stage'))))
    options.set('virtualenv', (lambda: '{dir}/virtualenv'.format(dir=fetch('shared_path'))))
    options.set('supervisord_pid', (lambda: '{dir}/tmp/pids/supervisord.pid'.format(dir=options.fetch('current_path'))))
    options.set('supervisord_conf', (lambda: '{dir}/supervisord.conf'.format(dir=options.fetch('current_path'))))
    options.set('pybundle_path', (lambda: '{dir}/system/konjak.pybundle'.format(dir=fetch('shared_path'))))
    
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
    
    @task
    @roles('app')
    def restart():
      with cd(fetch('current_path')):
        result = sudo("""
          (test -f {supervisord_pid} && kill -HUP `cat {supervisord_pid}`) || {virtualenv}/bin/supervisord -c {supervisord_conf}
        """.format(**var('virtualenv', 'supervisord_pid', 'supervisord_conf')), user=fetch('runner'))


## author

Yamashita, Yuu <yamashita@geishatokyo.com>
