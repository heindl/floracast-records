#!/usr/bin/env python
# encoding: utf-8

import unittest
# from florecords.features.terrain import Terrain
from florecords.features.landcover import Landcover
from florecords.features.request import FeatureRequest
from florecords.geo.cells import GenerateS2CellIds
from florecords.backport import timestamp
import datetime

# request_data = [
#     (
#         ('2015-01-02', 33.767, -84.560, 10),
#         {"landcover": "70", "slope": 2.0, "elevation": 239.0, "aspect": 161.0}
#     ),
#      (
#          ('2015-01-02', 38.6530169, -90.3835463, None),
#          {"slope": 4.0, "landcover": "50", "elevation": 194.0, "aspect": 285.0},
#      ),
#       (
#          ('2015-01-02', 34.7242069, -92.4780166, 1000),
#          {"slope": 4.3537854698384, "landcover": "55", "elevation": 165.78894432062955, "aspect": 153.34994171896417},
#      )
# ]


class TestEarthEngine(unittest.TestCase):

    def test_landcover(self):

        cell_id = GenerateS2CellIds(
            centre_lat=38.6530169,
            centre_lng=-90.3835463,
            uncertainty_threshold=6400,
           s2_cell_level=14
        )[0]
        req = FeatureRequest(
            observed_at=timestamp(datetime.datetime.utcnow()),
            cell_id=cell_id,
            occurrence_ids=[1]
        )

        for r in Landcover().fetch([req]):
            print(r)

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