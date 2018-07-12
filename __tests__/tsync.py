#!/usr/bin/env python
# encoding: utf-8

import unittest
from records.occurrences.sync import FetchOccurrenceSyncHistory
from records.cloud.utils import default_project
from records.occurrences.names import ScientificNameParser

class TestOccurrenceFetch(unittest.TestCase):

    def test_name_parser(self):
        parser = ScientificNameParser(
            project=default_project()
        )
        name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
        self.assertEqual(name, 'amanita augusta')
        parser._cache = {}
        name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
        self.assertEqual(name, 'amanita augusta')
        name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
        self.assertEqual(name, 'amanita augusta')

    def test_sync_history(self):
        docs = [x for x in FetchOccurrenceSyncHistory(default_project())]
        self.assertGreater(len(docs), 4)



if __name__ == '__main__':
    unittest.main()
