#!/usr/bin/env python
# encoding: utf-8

import unittest
from florecords.occurrences.compiler import OccurrenceCompiler
import numpy
import time


class TestGeometry(unittest.TestCase):

    def test_s2_cells(self):

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