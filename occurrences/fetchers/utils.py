#!/usr/bin/env python
# encoding: utf-8

import pandas
from datetime import datetime
from florecords.occurrences.taxa import NorthAmericanMacroFungiFamilies

class FetchParams(object):
    min_x, max_x, min_y, max_y = -180, 180, -90, 90
    observed_after, observed_before = "2002-01-01", datetime.now().strftime('%Y-%m-%d')
    updated_after, updated_before = "2002-01-01", datetime.now().strftime('%Y-%m-%d')
    family = ""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if self.family not in NorthAmericanMacroFungiFamilies:
            raise ValueError("Unrecognized fungi family: %s" % self.family)

def FilterOccurrenceDataframe(
    df, # type: pandas.DataFrame
    params, # type: FetchParams
):

    given_columns = df.columns.values

    for expected in [
        'name',
        'lat',
        'lng',
        'date',
        'modified',
        'id',
        'family',
        'source'
    ]:
        if expected not in given_columns:
            raise ValueError("Missing expected DataFrame column: %s" % expected)

    df.dropna(subset=[
        'name',
        'lat',
        'lng',
        'date',
        'id'
    ], inplace=True)

    df = df.assign(
        family = df.family.str.lower(),
        id = df.id.astype(dtype=str),
        modified = df.modified.str.slice(0, 10),
        date = df.date.str.slice(0, 10),
    )

    df = df[
        df.family.str.match(params.family, case=False) &
        (params.updated_after <= df.modified) &
        (df.modified <= params.updated_before) &
        (df.lat <= params.max_y) &
        (df.lat >= params.min_y) &
        (df.lng <= params.max_x) &
        (df.lng >= params.min_x) &
        (df.date >= params.observed_after) &
        (df.date <= params.observed_before)
    ]

    # Encode lat/lng to preserve precision
    df = df.assign(
        lat = df.lat.astype(dtype=str),
        lng = df.lng.astype(dtype=str),
    )

    return df

# def format_location(x):
#
#     distance = WGS84.Inverse(
#         x["latitude_south"],
#         x["longitude_west"],
#         x["latitude_north"],
#         x["longitude_east"]
#     )['s12']
#
#     if distance == 0:
#         return x.latitude_south, x.longitude_west, 0
#
#     g = WGS84.Direct(x["latitude_north"], x["longitude_east"], 225, distance/2)
#
#     return (g['lat2'],g['lon2'], distance)