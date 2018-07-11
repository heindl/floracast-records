#!/usr/bin/env python
# encoding: utf-8

import math
import numbers
from geographiclib.geodesic import Geodesic
WGS84 = Geodesic.WGS84
from s2_py import S2LatLng, S2LatLngRect, S2RegionCoverer, S2CellId, S2Cell
import ee
from records.occurrences.constants import STANDARD_S2_CELL_LEVEL, MAX_COORDINATE_UNCERTAINTY_METERS
from typing import Union, List
# import logging



def GeoJSONFeatureFromCellId(
        cell_id # type: S2CellId
    ):

    rect = S2Cell(cell_id).GetRectBound()

    bounds = (rect.lng_lo().degrees(), rect.lat_lo().degrees(), rect.lng_hi().degrees(), rect.lat_hi().degrees())

    return ee.Feature(
        geom=ee.Geometry.Rectangle(
            coords=bounds,
            proj='EPSG:4326',
            geodesic=True,
        ),
        opt_properties=ee.Dictionary({
            "cell_id": str(cell_id.id()) # Note this will error if not a string.
        }),
    )
def GenerateS2CellIds(
        centre_lat, # type: float
        centre_lng, # type: float
        coordinate_uncertainty=None, # type: Union[None, float]
        uncertainty_threshold=MAX_COORDINATE_UNCERTAINTY_METERS, # type: float
        s2_cell_level=STANDARD_S2_CELL_LEVEL, # type: int
    ): # type: (float, float, float, float, int) -> List[S2CellId]

    lat, lng, coordinate_uncertainty = NormalizeCoordinates(centre_lat, centre_lng, coordinate_uncertainty)

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

    return cell_ids

def NormalizeCoordinates(lat, lng, coordinate_uncertainty=None):
    if coordinate_uncertainty is not None and isinstance(coordinate_uncertainty, numbers.Number):
        return round(lat, 6), round(lng, 6), int(round(coordinate_uncertainty, 0))

    (lat_precision, lat_scale) = precision_and_scale(lat)
    (lng_precision, lng_scale) = precision_and_scale(lng)

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

def precision_and_scale(x):
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
