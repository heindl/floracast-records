#!/usr/bin/env python
# encoding: utf-8

import math
import numbers

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