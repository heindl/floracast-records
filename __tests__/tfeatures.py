#!/usr/bin/env python
# encoding: utf-8

import sys

import unittest
from ..features.landcover import Landcover
from ..geo import Cell
from ..occurrences import Occurrence
from ..utils import TimeStamp

class TestEarthEngine(unittest.TestCase):

    def test_landcover(self):

        occurrences = [Occurrence.decode({
            'source_key': 'gbif',
            'source_id': str(i),
            'name': 'Amanita fulva',
            'cell_id': int(cell_id.id()),
            'observed_at': TimeStamp.from_now()
        }) for i, cell_id in enumerate(Cell.from_coordinates(38.6530169, 90.3835463,1000))]

        r = Landcover().fetch(occurrences)
        print(r.bigquery_records)
        print([o.get_feature('landcover') for o in r.occurrences])

    # def test_terrain(self):
    #
    #     cell_id = GenerateS2CellIds(
    #         centre_lat=38.6530169,
    #         centre_lng=-90.3835463,
    #         uncertainty_threshold=6400,
    #         s2_cell_level=14
    #     )[0]
    #
    #     req = FeatureRequest(
    #         observed_at=timestamp(datetime.datetime.utcnow()),
    #         cell_id=cell_id,
    #         occurrence_ids=[1]
    #     )
    #
    #     for r in Terrain().fetch([req]):
    #         print(r)

    # def test_terrain_landcover_combined(self):
    #
    #     requests = map(lambda (i, r): FeatureRequest(
    #         observation_date=r[0][0],
    #         latitude=r[0][1],
    #         longitude=r[0][2],
    #         coordinate_uncertainty=r[0][3],
    #         occurrence_keys=[('gbif', i)],
    #         request_id=i
    #     ), enumerate(request_data))
    #
    #     requests = [r for r in Terrain().fetch(requests)]
    #     requests = [r for r in Landcover().fetch(requests)]
    #
    #     for i, r in enumerate(requests):
    #         t = request_data[i][1]
    #         for k in t:
    #             expect = t[k]
    #             actual = r.get_feature(k)
    #             self.assertEqual(
    #                 actual,
    #                 expect,
    #                 'Feature [%s] at request [%d] has value [%s] but expected [%s]' % (k, r.id(), actual, expect)
    #             )


if __name__ == '__main__':
    unittest.main()
