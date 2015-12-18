#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

from fabric.api import *
import fabric.contrib.project as project
import os

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
DEPLOY_PATH = env.deploy_path

# Remote server configuration
production = 'www-data@libc6.org:22'
dest_path = '/var/www/libc6.org/public'

# Rackspace Cloud Files configuration settings

def clean():
    if os.path.isdir(DEPLOY_PATH):
        local('rm -rf {deploy_path}'.format(**env))
        local('mkdir {deploy_path}'.format(**env))

def build():
    local('pelican -s pelicanconf.py')

def rebuild():
    clean()
    build()

def regenerate():
    local('pelican -r -s pelicanconf.py')

def serve():
    local('cd {deploy_path} && python -m SimpleHTTPServer'.format(**env))

def reserve():
    clean()
    build()
    serve()

def new(title, slug,overwrite="no"):
    from datetime import datetime 
    post_date = datetime.now().strftime("%Y-%m-%d")

    out_file = "content/{}.md".format(slug)
    out_template = "Title: %s\nSlug: %s\nCategory: Разное\nDate: %s\n\n" % (title, slug, post_date)
    if not os.path.exists(out_file) or overwrite.lower() == "yes":
        with open(out_file, 'w') as f:
            f.write(out_template.encode("utf-8"))
            f.close()
        local("vim %s"% out_file)
    else:
        print("{} already exists. Pass 'overwrite=yes' to destroy it.".
            format(out_file))

@hosts(production)
def publish():
    clean()
    build()
    project.rsync_project(
        remote_dir=dest_path,
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True
    )
