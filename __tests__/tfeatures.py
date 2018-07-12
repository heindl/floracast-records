#!/usr/bin/env python
# encoding: utf-8

import unittest
from features.landcover import Landcover
from occurrences import Occurrence
from utils import TimeStamp

class TestEarthEngine(unittest.TestCase):

    def test_landcover(self):

        occurrence = Occurrence.from_raw(
            source_id="1234",
            source_key="gbif",
            name="Amanita fulva",
            observed_at=TimeStamp.from_now(),
            lat=38.6530169,
            lng=90.3835463,
            coord_uncertainty=2000,
            family="amanitaceae"
        )
        self.assertIsNotNone(occurrence)

        expected_records = [
            {'cell_id': 4001881343356043264, 'landcover': {200: 2}},
            {'cell_id': 4001881472205062144, 'landcover': {200: 4}},
            {'cell_id': 4002054464897810432, 'landcover': {140: 2, 200: 2}},
            {'cell_id': 4001881351945977856, 'landcover': {200: 4}},
            {'cell_id': 4001881463615127552, 'landcover': {200: 4}},
            {'cell_id': 4002054473487745024, 'landcover': {200: 4}},
            {'cell_id': 4002054482077679616, 'landcover': {200: 4}},
            {'cell_id': 4002054507847483392, 'landcover': {200: 2}}
        ]

        landcover_response = Landcover().fetch([o for o in occurrence.split()])

        # Clear timestamp for comparison
        records = []
        for r in landcover_response.bigquery_records:
            del r['created_at']
            records.append(r)

        self.assertListEqual(
            sorted(records, key=lambda k: k['cell_id']),
            sorted(expected_records, key=lambda k: k['cell_id']),
        )

        self.assertListEqual(
            [o.get_feature('landcover') for o in landcover_response.occurrences],
            [{200: 2}, {200: 4}, {200: 4}, {200: 4}, {140: 2, 200: 2}, {200: 4}, {200: 4}, {200: 2}]
        )

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