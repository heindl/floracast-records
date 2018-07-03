#!/usr/bin/env python
# encoding: utf-8

import pandas
from datetime import datetime
from florecords.occurrences.constants import NorthAmericanMacroFungiFamilies
from florecords.occurrences.constants import MINIMUM_OCCURRENCE_TIME_SECONDS

class FetchParams(object):
    def __init__(self,
                 family, # type: str
                 min_x=-180, # type: float
                 max_x=180, # type: float
                 min_y=-90, # type: float
                 max_y=90, # type: float
                 observed_after=MINIMUM_OCCURRENCE_TIME_SECONDS, # type: int
                 observed_before=datetime.utcnow().timestamp(), # type: int
                 updated_after=datetime.utcnow().timestamp(), # type: int
                 updated_before=datetime.utcnow().timestamp(), # type: int
        ):
            self.family = family
            self.min_x = min_x
            self.max_x = max_x
            self.min_y = min_y
            self.max_y = max_y
            self.observed_after=observed_after
            self.observed_before=observed_before
            self.updated_after=updated_after
            self.updated_before=updated_before

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
        'observed_at',
        'modified_at',
        'source_id',
        'family',
        'source'
    ]:
        if expected not in given_columns:
            raise ValueError("Missing expected DataFrame column: %s" % expected)

    df.dropna(subset=[
        'name',
        'lat',
        'lng',
        'observed_at',
        'source_id'
    ], inplace=True)

    df = df.assign(
        family = df.family.str.lower(),
        source_id = df.source_id.astype(dtype=str),
        # modified = df.modified.str.slice(0, 10),
        # date = df.date.str.slice(0, 10),
    )

    df = df[
        df.family.str.match(params.family, case=False) &
        (params.updated_after <= df.modified_at) &
        (df.modified_at <= params.updated_before) &
        (df.lat <= params.max_y) &
        (df.lat >= params.min_y) &
        (df.lng <= params.max_x) &
        (df.lng >= params.min_x) &
        (df.observed_at >= params.observed_after) &
        (df.observed_at <= params.observed_before)
    ]

    # Encode lat/lng to preserve precision
    # df = df.assign(
    #     lat = df.lat.astype(dtype=str),
    #     lng = df.lng.astype(dtype=str),
    # )

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