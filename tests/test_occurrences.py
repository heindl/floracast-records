#!/usr/bin/env python
# encoding: utf-8

import numpy
from yoccurrences.generators import OccurrenceGenerators
import yoccurrences as occurrences
from yutils import default_project, TimeStamp
from typing import Generator, Union, Dict

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

def parse_fetch_response(occurrences):
    # type: (Generator[Union[occurrences.Occurrence, None]]) -> Dict

    res = []
    invalid_count = 0
    for o in occurrences:
        if o is None:
            invalid_count += 1
            continue
        res.append(len([o for o in o.split()]))

    res = numpy.array(res)
    return {
        'valid_count': len(res),
        'invalid_count': invalid_count, # coordinate uncertainty None response
        'total_cells': numpy.sum(res),
        'average_cells_per_occurrence': numpy.mean(res),
    }

_project = default_project()

def test_name_parser():
    parser = occurrences.ScientificNameParser(
        project=default_project()
    )
    name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
    assert name == 'amanita augusta'
    parser._cache = {}
    name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
    assert name == 'amanita augusta'
    name = parser.parse(name='Amanita augusta Bojantchev & R.M.Davis, 2013')
    assert name == 'amanita augusta'


def test_sync_history(self):

    src_key = 'gbif'
    family = 'amanitaceae'

    docs = occurrences.fetch_occurrence_sync_history(
        project=_project,
        source_key=src_key,
        restrict_families=[family]
    )
    self.assertEqual(len(docs), 1)

    original_ts = docs[0].fetched_at
    print('original sync timestamp', original_ts) # Keep in case the test fails to update the original.
    new_ts = TimeStamp.from_now()

    occurrences.register_occurrence_sync(
        project=_project,
        source_key=src_key,
        family=family,
        fetched_at=new_ts
    )

    docs = occurrences.fetch_occurrence_sync_history(
        project=_project,
        source_key=src_key,
        restrict_families=[family]
    )
    self.assertEqual(len(docs), 1)
    self.assertEqual(int(docs[0].fetched_at), new_ts)

    occurrences.register_occurrence_sync(
        project=_project,
        source_key=src_key,
        family=family,
        fetched_at=original_ts
    )


def test_idigbio():
    resp = parse_fetch_response(
        OccurrenceGenerators(['idigbio'])[0](**params).generate()
    )
    assert resp['valid_count'] == 17
    assert resp['invalid_count'] == 0
    assert resp['total_cells'] == 57
    assert resp['average_cells_per_occurrence'] == 3.3529411764705883


def test_gbif():
    resp = parse_fetch_response(
        OccurrenceGenerators(['gbif'])[0](**params).generate()
    )
    assert resp['valid_count'] == 298
    assert resp['invalid_count'] == 34
    assert resp['total_cells'] == 1657
    assert resp['average_cells_per_occurrence'] == 5.560402684563758


def test_inaturalist():
    resp = parse_fetch_response(
        OccurrenceGenerators(['inaturalist'])[0](**params).generate()
    )
    assert resp['valid_count'] == 388
    assert resp['invalid_count'] == 6
    assert resp['total_cells'] == 2173
    assert resp['average_cells_per_occurrence'] == 5.600515463917525


def test_mushroomobserver():
    resp = parse_fetch_response(
        OccurrenceGenerators(['mushroomobserver'])[0](**params).generate()
    )
    assert resp['valid_count'] == 673
    assert resp['invalid_count'] == 562
    assert resp['total_cells'] == 24548
    assert resp['average_cells_per_occurrence'] == 36.475482912332836


def test_mycoportal():
    resp = parse_fetch_response(
        OccurrenceGenerators(['mycoportal'])[0](**params).generate()
    )
    assert resp['valid_count'] == 1368
    assert resp['invalid_count'] == 11
    assert resp['total_cells'] == 2314
    assert resp['average_cells_per_occurrence'] == 1.6915204678362572