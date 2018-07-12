#!/usr/bin/env python
# encoding: utf-8

import google.auth
import constants
consts = constants.Constants()


# import os
# import subprocess

# export GOOGLE_CLOUD_PROJECT = ...

def default_project():

    credentials, project_id = google.auth.default()

    if project_id is not None and len(project_id) != 0:
        return project_id
    else:
        return consts['gcloud_project']

    # get_project = [
    #     'gcloud', 'config', 'list', 'project', '--format=value(core.project)'
    # ]
    #
    # with open(os.devnull, 'w') as dev_null:
    #     return subprocess.check_output(get_project, stderr=dev_null).strip()
