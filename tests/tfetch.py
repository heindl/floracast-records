#!/usr/bin/env python
# encoding: utf-8

import unittest, numpy
from occurrences.generators import OccurrenceGenerators
from occurrences import FetchOccurrenceSyncHistory, ScientificNameParser
from utils import default_project

params = {
    'min_y': 24.5465169,
    'min_x': -145.1767463,
    'max_y': 59.5747563,
    'max_x':-49.0,
    'observed_after': 1388534400, # "2014-01-01",
    'observed_before': 1420070400, # "2015-01-01",
    'updated_after': 1388534400, # "2014-01-01",
    'updated_before': 1514764800, # "2018-01-01",
    'family': "amanitaceae"
}

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
        docs = [x for x in FetchOccurrenceSyncHistory(
            project=default_project(),
            source='gbif',
            restrict_families=['agaricaceae']
        )]
        self.assertEqual(len(docs), 1)

    def test_gbif(self):
        parse(OccurrenceGenerators(['gbif'])[0].generate(**params))

    def test_idigb(self):
        parse(OccurrenceGenerators(['idigbio'])[0].generate(**params))

    def test_inat(self):
        parse(OccurrenceGenerators(['inaturalist'])[0].generate(**params))

    def test_mushroomobserver(self):
        parse(OccurrenceGenerators(['mushroomobserver'])[0].generate(**params))

    def test_mycoportal(self):
        parse(OccurrenceGenerators(['mycoportal'])[0].generate(**params))