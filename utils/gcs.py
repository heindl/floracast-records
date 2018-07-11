#!/usr/bin/env python
# encoding: utf-8

import google.auth



# import os
# import subprocess

# export GOOGLE_CLOUD_PROJECT = ...

def default_project():

    credentials, project_id = google.auth.default()

    return project_id

    # get_project = [
    #     'gcloud', 'config', 'list', 'project', '--format=value(core.project)'
    # ]
    #
    # with open(os.devnull, 'w') as dev_null:
    #     return subprocess.check_output(get_project, stderr=dev_null).strip()
