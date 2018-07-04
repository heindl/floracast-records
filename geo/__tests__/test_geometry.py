#!/usr/bin/env python
# encoding: utf-8

import unittest
from florecords.geo.cells import GenerateS2CellIds, DecodeCellIDAsGeoJSONRectangle


class TestGeometry(unittest.TestCase):

    def test_s2_cells(self):

        cell_ids = GenerateS2CellIds(35.8021685, -82.3451891, 6400, 14)
        self.assertEqual(len(cell_ids), 1)

        rect = DecodeCellIDAsGeoJSONRectangle(cell_ids[0])

        self.assertEqual(rect[0], -82.34518902474312)
        self.assertEqual(rect[1], 35.80182243257457)
        self.assertEqual(rect[2], -82.33976347120388)
        self.assertEqual(rect[3], 35.80759183314543)


if __name__ == '__main__':
    unittest.main()