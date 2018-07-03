#!/usr/bin/env python
# encoding: utf-8

import requests
import pandas
from florecords.occurrences.struct import Occurrence
from pandas.io.json.normalize import json_normalize
from florecords.occurrences.fetchers.utils import FilterOccurrenceDataframe, FetchParams
import math

# Note that most of these are nested json structs.
fields = [
    # "annotations",
    # "cached_votes_total",
    # "captive",
    # "comments",
    # "comments_count",
    # "community_taxon_id",
    # "created_at",
    # "created_at_details",
    # "created_time_zone",
    # "description",
    # "faves",
    # "faves_count",
    # "flags",
    # "geojson",
    # "geoprivacy",
    "id",
    # "id_please",
    # "identifications",
    # "identifications_count",
    # "identifications_most_agree",
    # "identifications_most_disagree",
    # "identifications_some_agree",
    # "license_code",
    "location",
    # "map_scale",
    # "mappable",
    # "non_owner_ids",
    # "num_identification_agreements",
    # "num_identification_disagreements",
    # "oauth_application_id",
    # "obscured",
    # "observation_photos",
    "observed_on",
    # "observed_on_details",
    # "observed_on_string",
    # "observed_time_zone",
    # "ofvs",
    # "out_of_range",
    # "outlinks",
    # "owners_identification_from_vision",
    # "photos",
    # "place_guess",
    # "place_ids",
    "positional_accuracy",
    # "preferences",
    # "project_ids",
    # "project_ids_with_curator_id",
    # "project_ids_without_curator_id",
    # "project_observations",
    # "public_positional_accuracy",
    # "quality_grade",
    # "quality_metrics",
    # "reviewed_by",
    # "site_id",
    # "sounds",
    # "spam",
    # "species_guess",
    # "tags",
    "taxon",
    # "time_observed_at",
    # "time_zone_offset",
    "updated_at",
    # "uri",
    # "user",
    # "uuid",
    # "votes",
]

def _taxon_id(family):

    url = 'https://api.inaturalist.org/v1/taxa'
    params = {
        'q': family.lower()
    }
    res = requests.get(url, params=params).json()
    for r in res['results']:
        if r['rank'] == 'family':
            return str(r['id'])

def _get_pages(
        params, # type: FetchParams,
        family_id # type: str
):

    q = {
        "per_page": 200,
        "has_name": True,
        "geo": True,
        "identified": True,
        "nelng": params.max_x,
        "nelat": params.max_y,
        "swlng": params.min_x,
        "swlat": params.min_y,
        "d1": params.observed_after,
        "d2": params.observed_before,
        "updated_since": params.updated_after,
        "taxon_id": family_id
        # "confidence": 2,
    }

    u = 'https://api.inaturalist.org/v1/observations'

    with requests.Session() as session:
        first_page = session.get(
            url=u,
            params=q
        ).json()

        if len(first_page['results']) == 0:
            return

        yield first_page["results"]

        num_pages = int(math.ceil(first_page["total_results"] / first_page['per_page']))

        for page in range(2, num_pages+1):
            pq = q.copy()
            pq['page'] = page
            next_page = session.get(url=u, params=pq).json()
            if len(next_page['results']) != 0:
                yield next_page['results']


def FetchOccurrences(
        params # type: FetchParams
):

    family_id = _taxon_id(params.family)

    for page in _get_pages(params, family_id):

        df = pandas.DataFrame.from_records(page, columns=fields)

        df.dropna(subset=[
            'taxon',
            'location',
        ], inplace=True)

        taxon = json_normalize(df.to_dict('list'), ['taxon']).apply(pandas.Series)[['name', 'ancestry']]

        location = df['location'].str.split(",").apply(pandas.Series)

        df = df.assign(
            name = taxon['name'],
            ancestry = taxon['ancestry'],
            lat = location[0].values.astype(dtype=float),
            lng = location[1].values.astype(dtype=float),
            source = lambda x: 'inaturalist',
            family = lambda x: params.family
        )

        df.rename(columns={
            'observed_on': 'date',
            'updated_at': 'modified',
            'positional_accuracy': 'coord_uncertainty',
        }, inplace=True)

        df = df[df.ancestry.str.contains(family_id)]

        df = FilterOccurrenceDataframe(df, params)

        for record in df.to_dict('records'):
            yield Occurrence(**record)