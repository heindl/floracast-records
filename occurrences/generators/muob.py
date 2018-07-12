#!/usr/bin/env python
# encoding: utf-8

import requests
import pandas
from ..occurrence import Occurrence
from pandas.io.json import json_normalize
from geographiclib.geodesic import Geodesic
WGS84 = Geodesic.WGS84
from .base import _BaseOccurrenceGenerator
from ...utils import TimeStamp

# Note that most of these are nested json structs.
fields = [
    "altitude",
    "collection_numbers",
    "comments",
    "confidence",
    "consensus",
    "created_at",
    "date",
    "herbarium_records",
    "id",
    "images",
    "is_collection_location",
    "last_viewed",
    "latitude",
    "location",
    "longitude",
    "namings",
    "notes",
    "notes_fields",
    "number_of_views",
    "owner",
    "primary_image",
    "sequences",
    "specimen_available",
    "type",
    "updated_at",
]

class _Generator(_BaseOccurrenceGenerator):

    @staticmethod
    def source_key():
        return 'mushroomobserver'

    @staticmethod
    def _format_location(x):

        distance = WGS84.Inverse(
            x["latitude_south"],
            x["longitude_west"],
            x["latitude_north"],
            x["longitude_east"]
        )['s12']

        if distance == 0:
            return x.latitude_south, x.longitude_west, 0

        g = WGS84.Direct(x["latitude_north"], x["longitude_east"], 225, distance/2)

        return (g['lat2'],g['lon2'], distance)

    def _get_pages(self):
        url = 'http://mushroomobserver.org/api/observations'

        q = {
            "format": 'json',
            "detail": "low",
            # "has_images": True,
            "has_name": True,
            "has_location": True,
            "is_collection_location": True,
            "east": self._max_x,
            "north": self._max_y,
            "west": self._min_x,
            "south": self._min_y,
            "date": '%s-%s' % (
                TimeStamp.format(self._observed_after, "%Y-%m-%d"),
                TimeStamp.format(self._observed_before, "%Y-%m-%d")
            ),
            "updated_at": '%s-%s' % (
                TimeStamp.format(self._updated_after, "%Y-%m-%d"),
                TimeStamp.format(self._updated_before, "%Y-%m-%d")
            ),
            "children_of": self._family
            # "confidence": 2,
        }

        with requests.Session() as session:
            first_page = session.get(url, params=q).json()
            yield first_page["results"]
            num_pages = first_page['number_of_pages']

            for page in range(2, num_pages + 1):
                p = q.copy()
                p['page'] = page
                next_page = session.get(url, params=p).json()
                yield next_page['results']


    def generate(self):

        for page in self._get_pages():

            df = pandas.DataFrame(page)

            location = json_normalize(df.to_dict('list'), ['location'])\
                .apply(pandas.Series)\
                .apply(self._format_location, axis=1)\
                .apply(pandas.Series)

            names = json_normalize(df.to_dict('list'), ['consensus']).apply(pandas.Series)['name'].values

            df = df[['id', 'date', 'updated_at']]

            df = df.assign(
                name = names,
                lat = location[0].values,
                lng = location[1].values,
                coord_uncertainty = location[2].values,
                source = lambda x: 'mushroomobserver',
                family = lambda x: self._family
            )

            df.rename(columns={
                'updated_at': 'modified_at',
                'date': 'observed_at',
                'id': 'source_id'
            }, inplace=True)

            # Convert to EpochTime
            df['observed_at']  = pandas.to_datetime(df['observed_at'])
            df['observed_at'] = (df['observed_at'] - pandas.Timestamp("1970-01-01")) // pandas.Timedelta('1s')

            df['modified_at']  = pandas.to_datetime(df['modified_at'])
            df['modified_at'] = (df['modified_at'] - pandas.Timestamp("1970-01-01")) // pandas.Timedelta('1s')

            df = self.filter_occurrence_dataframe(df)

            for record in df.to_dict('records'):
                yield Occurrence(**record)
