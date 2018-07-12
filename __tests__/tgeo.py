#!/usr/bin/env python
# encoding: utf-8

import unittest
from ..geo import cells


class TestGeometry(unittest.TestCase):

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
            r = cells.NormalizeCoordinates(q[0], q[1], q[2])
            for i in range(3):
                self.assertEqual(r[i], a[i])

    def test_s2_cells(self):

        cell_ids = cells.GenerateS2CellIds(35.8021685, -82.3451891, 6400, 14)
        self.assertEqual(len(cell_ids), 1)

        rect = DecodeCellIDAsGeoJSONRectangle(cell_ids[0])

        self.assertEqual(rect[0], -82.34518902474312)
        self.assertEqual(rect[1], 35.80182243257457)
        self.assertEqual(rect[2], -82.33976347120388)
        self.assertEqual(rect[3], 35.80759183314543)

    def test_s2_cells_2(self):

        for i, t in enumerate([
            (35.8021685, -82.3451891, numpy.nan, 1),
            (35.8021685, -82.3451891, 1000, 8),
            (35.8021685, -82.3451891, 2000, 120),
            (35.8021685, -82.3451891, 4000, 120),
            (35.8021685, -82.3451891, 8000, 120),
            (35.8021685, -82.3451891, 12000, 120),
            (35.8021685, -82.3451891, 16000, 120),
            (35.8021685, -82.3451891, 20000, 120),
            (35.8021685, -82.3451891, 22000, 120),
            (35.8021685, -82.3451891, 28000, 120),
            (35.8021685, -82.3451891, 32000, 120),
        ]):
            g = OccurrenceCompiler(
                id="1",
                scientific_name="Morchella delisiosa",
                observation_datetime=int(time.time()),
                coord_uncertainty=t[2],
                lat=t[0],
                lng=t[1],
                source="gbif",
                family="morchellaceae"
            )
            print(t[2], len(list(g.decompose())))


if __name__ == '__main__':
    unittest.main()
