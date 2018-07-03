#!/usr/bin/env python
# encoding: utf-8

import requests
import pandas
from florecords.occurrences.struct import Occurrence
from pandas.io.json.normalize import json_normalize
from geographiclib.geodesic import Geodesic
WGS84 = Geodesic.WGS84
from florecords.occurrences.fetchers.utils import FilterOccurrenceDataframe, FetchParams

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

def format_location(x):

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

def _get_pages(
        params # type: FetchParams
):
    url = 'http://mushroomobserver.org/api/observations'

    q = {
        "format": 'json',
        "detail": "low",
        # "has_images": True,
        "has_name": True,
        "has_location": True,
        "is_collection_location": True,
        "east": params.max_x,
        "north": params.max_y,
        "west": params.min_x,
        "south": params.min_y,
        "date": params.observed_after+"-"+params.observed_before,
        "updated_at": params.updated_after+'-'+params.updated_before,
        "children_of": params.family
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


def FetchOccurrences(
        params # type: FetchParams
):

    for page in _get_pages(params):

        df = pandas.DataFrame(page)

        location = json_normalize(df.to_dict('list'), ['location'])\
            .apply(pandas.Series)\
            .apply(format_location, axis=1)\
            .apply(pandas.Series)

        names = json_normalize(df.to_dict('list'), ['consensus']).apply(pandas.Series)['name'].values

        df = df[['id', 'date', 'updated_at']]

        df = df.assign(
            name = names,
            lat = location[0].values,
            lng = location[1].values,
            coord_uncertainty = location[2].values,
            source = lambda x: 'mushroomobserver',
            family = lambda x: params.family
        )

        df.rename(columns={
            'updated_at': 'modified',
        }, inplace=True)

        df = FilterOccurrenceDataframe(df, params)

        for record in df.to_dict('records'):
            yield Occurrence(**record)