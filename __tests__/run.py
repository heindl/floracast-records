from unittest import TestLoader, TextTestRunner, TestSuite
from .tfeatures import TestEarthEngine
from .tfetch import TestOccurrenceFetch

if __name__ == "__main__":

    loader = TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in (TestEarthEngine, TestOccurrenceFetch)
    ]
    suite = TestSuite(tests)

    runner = TextTestRunner(verbosity=2)
    runner.run(suite)