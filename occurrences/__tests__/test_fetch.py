#!/usr/bin/env python
# encoding: utf-8

import unittest
from florecords.occurrences.fetchers.utils import FetchParams
from florecords.occurrences.fetchers import gbif, idigb, inat, mycp, muob
from florecords.occurrences.sync import FetchOccurrenceSyncHistory
from florecords.cloud.utils import default_project
from florecords.occurrences.names import ScientificNameParser

params = FetchParams(
    min_y= 24.5465169,
    min_x= -145.1767463,
    max_y= 59.5747563,
    max_x=-49.0,
    observed_after="2014-01-01",
    observed_before="2015-01-01",
    updated_after="2014-01-01",
    updated_before="2018-01-01",
    family="amanitaceae"
)

class TestOccurrences(unittest.TestCase):

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

    def test_gbif(self):
        self.assertEqual(sum(1 for i in gbif.FetchOccurrences(params)), 331)
    #
    def test_idigb(self):
        self.assertEqual(sum(1 for i in idigb.FetchOccurrences(params)), 17)

    # def test_inat(self):
    #     self.assertEqual(sum(1 for i in inat.FetchOccurrences(params)), 649)
    #
    # def test_mushroomobserver(self):
    #     self.assertEqual(sum(1 for i in muob.FetchOccurrences(params)), 1227)

    # def test_mycoportal(self):
    #     self.assertEqual(sum(1 for i in mycp.FetchOccurrences(params)), 1379)


if __name__ == '__main__':
    unittest.main()