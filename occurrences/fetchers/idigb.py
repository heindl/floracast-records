#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import
from idigbio import pandas
import pandas as pd
from pandas.io.json import json_normalize
from florecords.occurrences.generator import OccurrenceGenerator
from florecords.occurrences.fetchers.utils import FilterOccurrenceDataframe, FetchParams
import datetime

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
    'datecollected',
    'datemodified',
    # 'eventdate', # Appears to be the same as datecollected,
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
                "gte": datetime.datetime.fromtimestamp(params.observed_after).strftime("%Y-%m-%d"),
                "lte": datetime.datetime.fromtimestamp(params.observed_before).strftime("%Y-%m-%d")
            },
            "datemodified": {
                "type": "range",
                "gte": datetime.datetime.fromtimestamp(params.updated_after).strftime("%Y-%m-%d"),
                "lte": datetime.datetime.fromtimestamp(params.updated_before).strftime("%Y-%m-%d")
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
        source_id=df.index.values
    )

    df.rename(
        columns={
            'scientificname': 'name',
            'datecollected': 'observed_at',
            'coordinateuncertainty': 'coord_uncertainty',
            'datemodified': 'modified_at'
        },
        inplace=True
    )

    # Convert to EpochTime
    df['observed_at']  = pd.to_datetime(df['observed_at'])
    df['observed_at'] = (df['observed_at'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

    df['modified_at']  = pd.to_datetime(df['modified_at'])
    df['modified_at'] = (df['modified_at'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

    df = FilterOccurrenceDataframe(df, params)

    for record in df.to_dict('records'):
        yield OccurrenceGenerator(**record)