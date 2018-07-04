#!/usr/bin/env python
# encoding: utf-8

import unittest
from pyflora.earthengine.terrain import Terrain

class TestEarthEngine(unittest.TestCase):

    def test_coordinate_format(self):

        for t in [
            [[44, -67, None], [44, -67, 111320]],
            [[44.87008, -67.1619, 3085.0], [44.87008, -67.1619, 3085]],
            [[32.66078,	-94.14483, 100.0], [32.66078, -94.14483, 100]],
            [[34.688, -81.4306, None], [34.688,	-81.4306, 111]],
            [[40.4355, -123.6724, None], [40.4355, -123.6724, 11]],
            [[40.4355123456, -123.6729485769, None], [40.435512, -123.672949, 0]]
        ]:
            q = t[0]
            a = t[1]
            r = FormatCoordinates(q[0], q[1], q[2])
            for i in range(3):
                self.assertEqual(r[i], a[i])

    def test_terrain(self):
        generator = Terrain()
        docs = [
                {
                    'latitude': 33.767,
                    'longitude': -84.560,
                    'coordinate_uncertainty': 10,
                },
                {
                    'latitude': 38.6530169,
                    'longitude': -90.3835463,
                    'coordinate_uncertainty': None,
                },
                {
                    'latitude': 34.7242069,
                    'longitude': -92.4780166,
                    'coordinate_uncertainty': 1000,
                },
        ]
        for doc in generator.fetch(docs):
            print(doc)


if __name__ == '__main__':
    unittest.main()