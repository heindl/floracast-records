#!/usr/bin/env python
# encoding: utf-8

# from geopy import Point
# from geopy.distance import vincenty

# class GeospatialBounds:
#     def __init__(self, lat=0, lng=0, radius_kilometers=0):
#         self._center = Point(lat, lng)
#         self._radius_kilometers = radius_kilometers
#
#     def from_coordinates(self, n, e, s, w):
#         ne = Point(n, e)
#         sw = Point(s, w)
#         radius = vincenty(sw, ne).kilometers / 2
#         center = vincenty(kilometers=radius).destination(sw, 45)
#         self._center = Point(center.latitude, center.longitude)
#         self._radius_kilometers = radius
#
#         return self
#
#     def extend_radius(self, additional_kilometers=0):
#         self._radius_kilometers = self._radius_kilometers + additional_kilometers
#
#     def _from_center(self, bearing):
#         return vincenty(kilometers=self._radius_kilometers).destination(self._center, bearing)
#
#     def north(self):
#         return self._from_center(0).latitude
#
#     def south(self):
#         return self._from_center(180).latitude
#
#     def east(self):
#         return self._from_center(90).longitude
#
#     def west(self):
#         return self._from_center(270).longitude


# Note that this may be an effective solution:
# https://github.com/GlobalNamesArchitecture/gnparser/blob/master/examples/jython/parser.py
# But using including a jar file maybe tough.
# There's also an api! So just include a filter DoFn.
# def parse_scientific_name(s):
#
# def PadCoord(coordinate_string, pad_str):
#
#     split = coordinate_string.split(".")
#     decimal_places = 0 if len(split) < 2 else len(split[1])
#
#     return '%s%s' % (coordinate_string, (7-decimal_places) * pad_str)

# class BoundingBox():
#     def __init__(self, sw, ne=None, within=None):
#
#         self._validate_coordinate(sw)
#
#         if within is not None:
#             assert (within.north() >= sw[0] <= within.south()), 'Point falls outside of Latitude bounds'
#             assert (within.west() >= sw[1] <= within.east()), 'Point falls outside of longitude bounds'
#
#         if ne is not None:
#             self._validate_coordinate(ne)
#             assert (sw[0] < ne[0]), 'First coordinate should be the SouthWest corner'
#             assert (sw[1] < ne[1]), 'First coordinate should be the SouthWest corner'
#             self._sw = sw
#             self._ne = ne
#             return
#
#         self._sw = (
#             self._add_precision(sw[0], '0'),
#             self._add_precision(sw[1], '9')
#         )
#
#         self._ne = (
#             self._add_precision(sw[0], '9'),
#             self._add_precision(sw[1], '0')
#         )
#
#     def north(self):
#         return float(self._ne[0])
#
#     def east(self):
#         return float(self._ne[1])
#
#     def south(self):
#         return float(self._sw[0])
#
#     def west(self):
#         return float(self._sw[1])
#
#     def rectangle(self):
#         return float(self._sw[0]), float(self._sw[1]), float(self._ne[0]), float(self._ne[1])
#
#     def _validate_coordinate(self, c):
#         assert isinstance(c, (list, tuple))
#         assert len(c) == 2
#         assert isinstance(c[0], str)
#         assert isinstance(c[1], str)
#         # assert (-180.0 > float(c[1]) and float(c[1]) < 180.0)
#         if -90.0 < float(c[0]) > 90:
#             raise ValueError('Invalid Coordinate Range')
#
#     def _add_precision(self, coordinate_string, pad_number_str='0'):
#
#         split = coordinate_string.split(".")
#         decimal_places = 0 if len(split) < 2 else len(split[1])
#
#         return '%s%s' % (coordinate_string, (7-decimal_places) * pad_number_str)
