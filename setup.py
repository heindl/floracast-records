import setuptools
import os
from setuptools.command.build_py import build_py as _build_py
import subprocess
import distutils

# 1063757818890-compute@developer.gserviceaccount.com

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
                'cmake',
                'openssl',
                'libgtest-dev',
                'git',
                'libgflags-dev',
                'libgoogle-glog-dev',
                'libssl-dev',
                'swig'
            ])

            # honor the --dry-run flag
            if not self.dry_run:

                ee_config_path = '~/.config/earthengine/'

                if os.path.exists(ee_config_path):
                    print('EarthEngine config path exists.')
                else:
                    os.makedirs(ee_config_path)
                    with open(ee_config_path + 'credentials', 'w') as fobj:
                        fobj.write('{"refresh_token": "1/M6a80JfcGRgczCRftwne_bclodJlYJ9z1XaXJXHbrPI"}')

        # distutils uses old-style classes, so no super()
        _build_py.run(self)

if __name__ == '__main__':

    setuptools.setup(
        name='florecords',
        version='0.0.1',
        description='Files for compiling Floracast prediction data',
        packages=setuptools.find_packages(),
        url="https://bitbucket.org/heindl/florecords",
        author="mph",
        author_email="matt@floracast.com",
        cmdclass={
            # Command class instantiated and run during pip install scenarios.
            'build_py': build_py,
        },
        install_requires=[
            "geographiclib",
            "httplib2",
            "idigbio",
            "numpy",
            "pandas",
            "pygbif",
            "requests",
            "typing",
            "google-auth",
            'google-api-python-client',
            "google-cloud-firestore",
            'pyCrypto',
            'earthengine-api',
            's2_py'
        ]
    )
