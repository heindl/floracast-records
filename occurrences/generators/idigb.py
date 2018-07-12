#!/usr/bin/env python
# encoding: utf-8

from idigbio import pandas
import pandas as pd
from pandas.io.json import json_normalize
from .. import Occurrence
from utils import TimeStamp
from .base import BaseOccurrenceGenerator

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

class Generator(BaseOccurrenceGenerator):

    @staticmethod
    def source_key():
        return 'idigbio'

    def generate(self):

        api = pandas()

        df = api.search_records(
            rq={
                "eventdate": {
                    "type": "range",
                    "gte": TimeStamp.format(self._observed_after, "%Y-%m-%d"),
                    "lte": TimeStamp.format(self._observed_before, "%Y-%m-%d"),
                },
                "datemodified": {
                    "type": "range",
                    "gte": TimeStamp.format(self._updated_after, "%Y-%m-%d"),
                    "lte": TimeStamp.format(self._updated_before, "%Y-%m-%d")
                },
                "geopoint": {
                    "type": "geo_bounding_box",
                    "top_left": {
                        "lat": self._max_y,
                        "lon": self._min_x
                    },
                    "bottom_right": {
                        "lat": self._min_y,
                        "lon": self._max_x
                    }
                },
                "family": self._family,
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
            source_key=lambda x: 'idigbio',
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

        df = self.filter_occurrence_dataframe(df)

        for record in df.to_dict('records'):
            yield Occurrence.from_raw(**record)
