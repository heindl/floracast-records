#!/usr/bin/env python
# encoding: utf-8

import unittest
from ..occurrences.fetchers.utils import FetchParams
from ..occurrences.fetchers import gbif, idigb, inat, mycp, muob
from ..occurrences.fetch import FetchOccurrences
from ..occurrences.names import ScientificNameParser
from ..occurrences import sync
from ..utils import gcs
import numpy

params = FetchParams(
    min_y= 24.5465169,
    min_x= -145.1767463,
    max_y= 59.5747563,
    max_x=-49.0,
    observed_after=1388534400, # "2014-01-01",
    observed_before=1420070400, # "2015-01-01",
    updated_after=1388534400, # "2014-01-01",
    updated_before=1514764800, # "2018-01-01",
    family="amanitaceae"
)

def parse(generated):

    res = []
    capped = 0
    for i in generated:
        cells = i.decompose()
        if len(cells) == 0:
            capped += 1
            continue
        res.append(len(cells))

    res = numpy.array(res)
    print("capped", capped)
    print("processed", len(res))
    print("sum", numpy.sum(res))
    print("average", numpy.mean(res))

class TestOccurrenceFetch(unittest.TestCase):

    def test_name_parser(self):
        parser = ScientificNameParser(
            project=gcs.default_project()
        )
        name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
        self.assertEqual(name, 'amanita augusta')
        parser._cache = {}
        name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
        self.assertEqual(name, 'amanita augusta')
        name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
        self.assertEqual(name, 'amanita augusta')

    def test_sync_history(self):
        docs = [x for x in sync.FetchOccurrenceSyncHistory(
            project=gcs.default_project(),
            source='gbif',
            restrict_families=['agaricaceae']
        )]
        self.assertEqual(len(docs), 1)

    def test_gbif(self):
        parse(gbif.FetchOccurrences(params))

    def test_idigb(self):
        parse(idigb.FetchOccurrences(params))

    def test_inat(self):
        parse(inat.FetchOccurrences(params))

    def test_mushroomobserver(self):
        parse(muob.FetchOccurrences(params))

    def test_mycoportal(self):
        parse(mycp.FetchOccurrences(params))

    def test_fetch(self):
        parse(FetchOccurrences(params, sources=[
            'idigbio',
        ]))


if __name__ == '__main__':
    unittest.main()
