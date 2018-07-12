#!/usr/bin/env python
# encoding: utf-8

import unittest, numpy
from geo import Cell
import constants


class TestGeo(unittest.TestCase):

    def test_coordinate_normalization(self):

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
            r = Cell.normalize_coordinates(q[0], q[1], q[2])
            for i in range(3):
                self.assertEqual(r[i], a[i])

    def test_cell_generation_from_coordinates_at_one_level(self):

        cells = Cell.from_coordinates(
            lat=35.8021685,
            lng=-82.3451891,
            s2_cell_level=14,
        )
        self.assertEqual(len(cells), 1)
        rect = cells[0].bounds()
        self.assertEqual(rect[0], -82.34518902474312)
        self.assertEqual(rect[1], 35.80182243257457)
        self.assertEqual(rect[2], -82.33976347120388)
        self.assertEqual(rect[3], 35.80759183314543)

    def test_constants(self):

        consts = constants.Constants()
        self.assertEqual(consts['standard_s2_cell_level'], 14)
        self.assertEqual(consts['max_coordinate_uncertainty_meters'], 7000)

        self.assertEqual(len(Cell.from_coordinates(
            lat=35.8021685,
            lng=-82.3451891,
            uncertainty_meters=4000,
        )), 48)

        self.assertEqual(len(Cell.from_coordinates(
            lat=35.8021685,
            lng=-82.3451891,
            uncertainty_meters=18000,
        )), 0)

    def test_cell_generation_at_level_fourteen(self):

        for i, t in enumerate([
            (35.8021685, -82.3451891, numpy.nan, 1),
            (35.8021685, -82.3451891, 1000, 8),
            (35.8021685, -82.3451891, 2000, 8),
            (35.8021685, -82.3451891, 4000, 48),
            (35.8021685, -82.3451891, 7000, 148),
            (35.8021685, -82.3451891, 8000, 196),
            (35.8021685, -82.3451891, 10000, 308),
            (35.8021685, -82.3451891, 12000, 454),
            (35.8021685, -82.3451891, 16000, 817),
            (35.8021685, -82.3451891, 20000, 1285),
            (35.8021685, -82.3451891, 22000, 1563),
            (35.8021685, -82.3451891, 28000, 2543),
            (35.8021685, -82.3451891, 32000, 3335),
        ]):
            cells = Cell.from_coordinates(
                lat=t[0],
                lng=t[1],
                uncertainty_meters=t[2],
                uncertainty_threshold=32000,
                s2_cell_level=14,
            )
            self.assertEqual(len(cells), t[3])

    def test_cell_generation_at_level_sixteen(self):

        for i, t in enumerate([
            (35.8021685, -82.3451891, numpy.nan, 1),
            (35.8021685, -82.3451891, 1000, 8),
            (35.8021685, -82.3451891, 2000, 48),
            (35.8021685, -82.3451891, 4000, 196),
            (35.8021685, -82.3451891, 8000, 817),
            (35.8021685, -82.3451891, 12000, 0),
        ]):
            cells = Cell.from_coordinates(
                lat=t[0],
                lng=t[1],
                uncertainty_meters=t[2],
                uncertainty_threshold=8000,
                s2_cell_level=15,
            )
            self.assertEqual(len(cells), t[3])


if __name__ == '__main__':
    unittest.main()
