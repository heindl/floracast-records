#!/usr/bin/env python
# encoding: utf-8

import ee
from . import BaseFeatureGenerator, FeatureResponse
from occurrences import CompileOccurrenceSQLQuery, Occurrence
from geo import Cell
from utils import TimeStamp
from typing import List, Tuple, Union
import collections

class Landcover(BaseFeatureGenerator):

    @staticmethod
    def table_name():
        return 'LandCover'

    @staticmethod
    def schema():
        return [
            {
                "name": "cell_id",
                "type": "FLOAT",
                "mode": "REQUIRED"
            },
            {
                "name": "landcover",
                "type": "RECORD",
                "mode": "REPEATED",
                "fields": [
                    {
                        "name": "id",
                        "type": "INTEGER",
                        "mode": "REQUIRED"
                    },
                    {
                        "name": "count",
                        "type": "INTEGER",
                        "mode": "REQUIRED"
                    },
                ],
            },
            {
                "name": "created_at",
                "type": "TIMESTAMP",
                "mode": "REQUIRED"
            }
        ]

    @staticmethod
    def query(table):
        return CompileOccurrenceSQLQuery(table)

    @staticmethod
    def is_complete(o): # type: (Occurrence) -> bool
        return o.get_feature('landcover') is not None

    @staticmethod
    def partition_key(o): # type: (Occurrence) -> str
        return str(o.cell().parent(7))

    @staticmethod
    def combine(t):
        # type: (Tuple[Tuple[str, str], List[Occurrence]]) -> Union[None, Occurrence]

        _, occurrences = t

        features = [o.get_feature('landcover') for o in occurrences]

        res = {}
        for feature in features:
            # Important that all cells are accounted for.
            if feature is None:
                return None
            for id, count in feature:
                if id in res:
                    res[id] += count
                else:
                    res[id] = count
        o = occurrences[0]
        o.set_feature('landcover', res)
        return o

    @staticmethod
    def fetch(occurrences): # type: (List[Occurrence]) -> FeatureResponse

        unique_cell_ids = set([r.cell().id() for r in occurrences])

        fc = ee.FeatureCollection(
            [Cell(id).geojson_feature() for id in unique_cell_ids]
        )

        img = ee.Image('ESA/GLOBCOVER_L4_200901_200912_V2_3').select('landcover')
        regions = img.reduceRegions(
            reducer=ee.Reducer.toList().setOutputs(['landcover']),
            collection=fc,
        )

        bigquery_values = []

        for f in regions.getInfo()['features']:
            props = f['properties']
            value = dict(collections.Counter(props['landcover']))

            bigquery_values.append({
                'cell_id': int(props['cell_id']),
                'created_at': TimeStamp.from_now(),
                'landcover': value,
            })
            for o in occurrences:
                if str(o.cell()) == props['cell_id']:
                    o.set_feature('landcover', value)

        return FeatureResponse(
            bigquery_records=bigquery_values,
            occurrences = occurrences
        )
