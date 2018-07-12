#!/usr/bin/env python
# encoding: utf-8

import math, numbers, numpy
from geographiclib.geodesic import Geodesic
WGS84 = Geodesic.WGS84
from s2_py import S2LatLng, S2LatLngRect, S2RegionCoverer, S2CellId, S2Cell
import ee
import constants
consts = constants.Constants()
from typing import Union, List


class Cell(S2CellId):

    def __repr__(self):
        return str(self.id())

    def __str__(self):
        return str(self.id())

    def bounds(self):
        rect = S2Cell(self).GetRectBound()
        return (
            rect.lng_lo().degrees(),
            rect.lat_lo().degrees(),
            rect.lng_hi().degrees(),
            rect.lat_hi().degrees()
        )

    def geojson_feature(self):
        return ee.Feature(
            geom=ee.Geometry.Rectangle(
                coords=self.bounds(),
                proj='EPSG:4326',
                geodesic=True,
            ),
            opt_properties=ee.Dictionary({
                "cell_id": str(self) # Note this will error if not a string.
            }),
        )

    @classmethod
    def from_coordinates(
        cls,
        lat,
        lng,
        uncertainty_meters=None,
        uncertainty_threshold=consts['max_coordinate_uncertainty_meters'],
        s2_cell_level=consts['standard_s2_cell_level'],
    ): # type: (float, float, Union[None, numpy.nan, numbers.Number], float, int) -> List[Cell]

        lat, lng, coordinate_uncertainty = Cell.normalize_coordinates(lat, lng, uncertainty_meters)

        if coordinate_uncertainty > uncertainty_threshold:
            return []

        radius = coordinate_uncertainty / 2

        w = WGS84.Direct(lat, lng, 270, radius)['lon2']
        n = WGS84.Direct(lat, lng, 0, radius)['lat2']
        e = WGS84.Direct(lat, lng, 90, radius)['lon2']
        s = WGS84.Direct(lat, lng, 180, radius)['lat2']

        rectangle = S2LatLngRect(
            S2LatLng.FromDegrees(s, w),
            S2LatLng.FromDegrees(n, e),
        )

        # print("area", rectangle.Area() / 12.56637 * 510072000000)

        region = S2RegionCoverer()
        region.set_max_cells(10000) # Irrelevant number but necessary because it appears to cap cells to 8.
        region.set_min_level(s2_cell_level)
        region.set_max_level(s2_cell_level)

        cell_ids = region.GetInteriorCovering(rectangle)
        if len(cell_ids) == 0:
            cell_ids = region.GetCovering(rectangle)

        # logging.info("S2 Covering [%d] Generated [%f, %f, %f]", len(cell_ids), lat, lng, coordinate_uncertainty)

        return [cls(c.id()) for c in cell_ids]

    @staticmethod
    def normalize_coordinates(lat, lng, uncertainty=None):
        # type: (float, float, Union[None, numpy.nan, numbers.Number]) -> (float, float, float)

        valid_uncertainty = uncertainty is not None \
                          and uncertainty is not numpy.nan \
                          and isinstance(uncertainty, numbers.Number)

        if valid_uncertainty:
            return round(lat, 6), round(lng, 6), int(round(uncertainty, 0))

        (lat_precision, lat_scale) = _precision_and_scale(lat)
        (lng_precision, lng_scale) = _precision_and_scale(lng)

        min_scale = min([lat_scale, lng_scale])

        if min_scale >= 6:
            return (round(lat, 6), round(lng, 6), 0)

        equatorial_precision_in_meters = [
            111320,
            11132,
            1113,
            111,
            11,
            1,
        ]

        return (lat, lng, equatorial_precision_in_meters[min_scale])

def _precision_and_scale(x):
    max_digits = 14
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return (magnitude, 0)
    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))
    return (magnitude + scale, scale)
