from unittest import TestLoader, TextTestRunner, TestSuite

import os, sys

# PACKAGE_PARENT = '...'
# SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
#
# print('script_dir', SCRIPT_DIR)
# sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

os.environ['__CONSTANTS__'] = 'test'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print('from_run', sys.path)

from tests.tfeatures import TestEarthEngine
from tests.tfetch import TestOccurrenceFetch
from tests.tgeo import TestGeometry

if __name__ == "__main__":

    loader = TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in (TestGeometry, TestEarthEngine, TestOccurrenceFetch)
    ]
    suite = TestSuite(tests)

    runner = TextTestRunner(verbosity=2)
    runner.run(suite)