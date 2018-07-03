#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import
from idigbio import pandas
import pandas as pd
from pandas.io.json import json_normalize
from florecords.occurrences.struct import Occurrence
from florecords.occurrences.fetchers.utils import FilterOccurrenceDataframe, FetchParams

FIELDS = [
    'uuid',
    # 'basisofrecord',
    # 'canonicalname',
    # 'catalognumber',
    # 'class',
    # 'collectioncode',
    # 'collectionid',
    # 'collector',
    # 'continent',
    'coordinateuncertainty',
    # 'country',
    # 'countrycode',
    # 'county',
    # 'datasetid',
    # 'datecollected',
    'datemodified',
    'eventdate', # Appears to be the same as datecollected,
                   # except NaN when the event date is in the early part of last center.
    # 'verbatimeventdate', # Mostly missing or non-specific
    # 'dqs', # Believe this is a data quality score.
    # 'etag', # Believe to be a unique identifier, but will use IDigBio uuid.
    'family',
    # 'flags',
    # 'genus',
    'geopoint',
    # 'hasImage',
    # 'hasMedia',
    # 'highertaxon',
    # 'indexData', # Info organized into search field.
    # 'institutioncode',
    # 'kingdom',
    # 'locality', # Mostly missing or non-specific
    # 'mediarecords',
    # 'minelevation',
    # 'municipality',
    # 'occurrenceid',
    # 'order',
    # 'phylum',
    # 'recordids',
    # 'recordnumber', # Appears to be useless, tied to recordset.
    # 'recordset',
    'scientificname',
    # 'specificepithet',
    # 'startdayofyear',
    # 'stateprovince',
    # 'taxonid',
    # 'taxonomicstatus',
    # 'taxonrank',
    # 'typestatus',
 ]

def FetchOccurrences(
        params # type: FetchParams
):

    api = pandas()

    df = api.search_records(
        rq={
            "eventdate": {
                "type": "range",
                "gte": params.observed_after,
                "lte": params.observed_before
            },
            "datemodified": {
                "type": "range",
                "gte": params.updated_after,
                "lte": params.updated_before
            },
            "geopoint": {
                "type": "geo_bounding_box",
                "top_left": {
                    "lat": params.max_y,
                    "lon": params.min_x
                },
                "bottom_right": {
                    "lat": params.min_y,
                    "lon": params.max_x
                }
            },
            "family": params.family,
        },
        fields=[x for x in FIELDS]
    )

    df.dropna(subset=[
        'geopoint',
    ], inplace=True)

    coords = json_normalize(df.to_dict('list'), ['geopoint']).apply(pd.Series)

    df = df.assign(
        lat=coords['lat'].values,
        lng=coords['lon'].values,
        source=lambda x: 'idigbio',
        id=df.index.values
    )

    df.rename(
        columns={
            'scientificname': 'name',
            'eventdate': 'date',
            'coordinateuncertainty': 'coord_uncertainty',
            'datemodified': 'modified'
        },
        inplace=True
    )

    df = FilterOccurrenceDataframe(df, params)

    for record in df.to_dict('records'):
        yield Occurrence(**record)