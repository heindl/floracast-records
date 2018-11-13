#!/usr/bin/env python
# encoding: utf-8
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import setuptools
import os
from setuptools.command.build_py import build_py as _build_py
import subprocess
# import distutils
import io
import re
from glob import glob
from os.path import basename, splitext
# from os.path import dirname
# from os.path import join


# def get_version():
#     global_names = {}
#     exec(open(os.path.normpath('./apache_beam/version.py')).read(), global_names)  # pylint: disable=exec-used
#     return global_names['__version__']

class build_py(_build_py):

    def _run_subprocess(self, command_list):
        p = subprocess.Popen(
            command_list,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        # Can use communicate(input='y\n'.encode()) if the command run requires
        # some confirmation.
        stdout_data, _ = p.communicate()
        print('Command output: %s' % stdout_data)
        if p.returncode != 0:
            raise RuntimeError(
                'Command %s failed: exit code: %s' % (command_list, p.returncode)
            )

    def _apt_get(self, packages):
        self._run_subprocess(['apt-get', 'update'])
        for package in packages:
            print('Installing Package: %s' % package)
            self._run_subprocess(['apt-get', '--assume-yes', 'install', package])

    def run(self):

        if distutils.spawn.find_executable("apt-get") is not None:

            self._apt_get([
                # 'cmake',
                # 'openssl',
                'libgtest-dev',
                # 'git',
                # 'libgflags-dev',
                # 'libgoogle-glog-dev',
                # 'libssl-dev',
                'swig'
            ])

            # honor the --dry-run flag
            # if not self.dry_run:
            #
            #     ee_config_path = '~/.config/earthengine/'
            #
            #     if os.path.exists(ee_config_path):
            #         print('EarthEngine config path exists.')
            #     else:
            #         os.makedirs(ee_config_path)
            #         with open(ee_config_path + 'credentials', 'w') as fobj:
            #             fobj.write('{"refresh_token": "1/M6a80JfcGRgczCRftwne_bclodJlYJ9z1XaXJXHbrPI"}')

        # distutils uses old-style classes, so no super()
        _build_py.run(self)

if __name__ == '__main__':

    setuptools.setup(
        name='florecords',
        version='0.0.1',
        description='Files for compiling Floracast prediction data',
        packages=setuptools.find_packages('src'),
        package_dir={'': 'src'},
        author="mph",
        author_email="matt@floracast.com",
        py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
        include_package_data=True,
        url="https://bitbucket.org/floracast/florecords",
        # zip_safe=False,
        cmdclass={
            # Command class instantiated and run during pip install scenarios.
            'build_py': build_py,
        },
        # Note: Check here for any dependencies that already exist in dataflow,
        # which will speed up the setup process: https://cloud.google.com/dataflow/docs/concepts/sdk-worker-dependencies.
        # All local testing should happen on the preloaded docker machine.
        install_requires=[
            "cmake"
        ],
        tests_require = ['pytest'],
    )
